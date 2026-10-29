const form = document.querySelector(".composer");
const text = form.elements.text;
const send = form.querySelector(".send");
const picker = form.querySelector("input[type=file]");
const attachment = form.querySelector(".attachment");
const problem = document.querySelector(".problem");
const report = document.querySelector(".report");
const newCheck = document.querySelector(".new-check");
const note = document.querySelector(".note");
const icons = document.querySelector("#verdict-icons").content;

const IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const LABELS = { true: "True", false: "False", misleading: "Misleading", unverifiable: "Unverified" };
const touch = matchMedia("(pointer: coarse)").matches;

let image = null; // { data: base64, type, url }
let busy = false;
let running = null; // AbortController of the check in progress

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

const icon = (selector) => icons.querySelector(selector).cloneNode(true);
const host = (url) => new URL(url).hostname.replace(/^www\./, "");
const empty = () => document.body.classList.contains("empty");
const transition = (change) => (document.startViewTransition ? document.startViewTransition(change) : change());

function update() {
  send.disabled = busy || !(text.value.trim() || image);
}

// Only while the composer shows: a hidden textarea measures 0 and would stay collapsed.
function fit() {
  text.style.height = "auto";
  text.style.height = `${text.scrollHeight}px`;
}

function say(message) {
  problem.textContent = message;
  problem.hidden = !message;
}

async function attach(file) {
  if (!IMAGE_TYPES.includes(file.type)) return say("Screenshots must be PNG, JPG or WebP.");
  if (file.size > MAX_IMAGE_BYTES) return say("Screenshots must be under 5 MB.");
  const data = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.readAsDataURL(file);
  });
  detach();
  image = { data, type: file.type, url: URL.createObjectURL(file) };
  attachment.prepend(el("img", { src: image.url, alt: "Screenshot to check" }));
  attachment.hidden = false;
  say("");
  update();
}

function detach() {
  attachment.querySelector("img")?.remove();
  attachment.hidden = true;
  image = null;
  update();
}

function linkify(reply) {
  return reply
    .split(/(https?:\/\/[^\s<>()]*[^\s<>().,!?;:'"])/g)
    .map((part, i) => (i % 2 ? el("a", { href: part, textContent: part, target: "_blank", rel: "noopener" }) : part));
}

// Long messages fold to four lines (see .message p), with a toggle only when something is hidden.
function fold(quote) {
  const p = quote.querySelector("p");
  if (!p || p.scrollHeight <= p.clientHeight) return;
  const more = el("button", { type: "button", className: "more", textContent: "Show all" });
  more.setAttribute("aria-expanded", "false");
  more.onclick = () => {
    const whole = quote.classList.toggle("whole");
    more.textContent = whole ? "Show less" : "Show all";
    more.setAttribute("aria-expanded", String(whole));
  };
  quote.append(more);
}

function claim(result) {
  const badge = el("span", { className: "badge" }, icon(`[data-verdict="${result.verdict}"]`), LABELS[result.verdict]);
  badge.dataset.verdict = result.verdict;
  const sources = result.sources
    .filter((s) => /^https?:\/\//.test(s.url))
    .map((s) => el("li", {},
      el("a", { href: s.url, textContent: s.title || host(s.url), target: "_blank", rel: "noopener" }),
      el("span", { className: "domain", textContent: host(s.url) })));
  const meta = `Confidence ${Math.round(result.confidence * 100)}%` + (result.from_memory ? " · from an earlier check" : "");
  return el("li", {}, el("details", {},
    el("summary", {}, badge, el("span", { className: "claim", textContent: result.claim }), icon('[data-icon="chevron"]')),
    el("div", { className: "evidence" },
      el("p", { textContent: result.rationale }),
      ...(sources.length ? [el("ul", { className: "sources" }, ...sources)] : []),
      el("p", { className: "meta", textContent: meta }))));
}

function answer({ reply, results }) {
  const label = el("span", { textContent: "Copy reply" });
  const copy = el("button", { type: "button", className: "copy" }, icon('[data-icon="copy"]'), label);
  copy.onclick = async () => {
    try {
      await navigator.clipboard.writeText(reply);
      copy.firstChild.replaceWith(icon('[data-verdict="true"]'));
      label.textContent = "Copied";
    } catch {
      label.textContent = "Couldn't copy";
    }
    setTimeout(() => {
      copy.firstChild.replaceWith(icon('[data-icon="copy"]'));
      label.textContent = "Copy reply";
    }, 2000);
  };
  // Nothing was checked: no reply worth sending back, and no verdicts or sources to caution about.
  note.hidden = !results.length;
  const parts = [el("p", { className: "reply" }, ...linkify(reply))];
  if (results.length) parts.push(copy, el("ul", { className: "claims" }, ...results.map(claim)));
  return parts;
}

async function* lines(body) {
  const reader = body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) return;
    const parts = (buffer + value).split("\n");
    buffer = parts.pop();
    for (const part of parts) if (part) yield JSON.parse(part);
  }
}

function fail(out, message, payload) {
  out.removeAttribute("aria-busy");
  out.replaceChildren(el("p", { className: "failed", textContent: message }));
  if (payload) {
    out.append(el("button", { type: "button", className: "retry", textContent: "Try again", onclick: () => check(payload, out) }));
  }
}

async function check(payload, out) {
  const controller = (running = new AbortController());
  busy = true;
  newCheck.hidden = true;
  note.hidden = true;
  update();
  const label = el("span", { textContent: "Reading the message…" });
  const steps = el("ol");
  const progress = el("details", { className: "progress" }, el("summary", {}, label, icon('[data-icon="chevron"]')), steps);
  progress.dataset.running = "";
  out.setAttribute("aria-busy", "true");
  out.replaceChildren(progress);
  const started = Date.now();
  try {
    const response = await fetch("/api/checks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (response.status === 429) return fail(out, "You've reached today's limit. Please try again tomorrow.");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    let done = false;
    for await (const event of lines(response.body)) {
      if (event.error) throw new Error(event.error);
      if (event.step) {
        label.textContent = `${event.step}…`;
        if (![...steps.children].some((s) => s.textContent === event.step)) steps.append(el("li", { textContent: event.step }));
      } else {
        delete progress.dataset.running;
        label.textContent = `Checked in ${Math.round((Date.now() - started) / 1000)}s`;
        out.append(...answer(event));
        out.removeAttribute("aria-busy");
        done = true;
      }
    }
    if (!done) throw new Error("Stream ended early");
  } catch {
    if (!controller.signal.aborted) fail(out, "Something went wrong.", payload);
  } finally {
    // A check the reader left (Back) must not touch the page that replaced it.
    if (running === controller) {
      running = null;
      busy = false;
      update();
      transition(() => (newCheck.hidden = false));
    }
  }
}

// Each check stands alone: it replaces the page and gets its own history entry, so Back starts over.
function submit(message, screenshot) {
  if (busy) return;
  busy = true; // now, not in the transition: a held Enter must not start a second check
  update();
  history.pushState({ check: true }, "");
  transition(() => {
    document.body.classList.remove("empty");
    const quote = el("blockquote", { className: "message" });
    if (screenshot) quote.append(el("img", { src: screenshot.url, alt: "Screenshot sent for checking" }));
    if (message) quote.append(el("p", { textContent: message }));
    const out = el("div", { className: "result" });
    report.replaceChildren(quote, out);
    fold(quote);
    text.value = "";
    text.style.height = ""; // back to one row
    detach();
    say("");
    if (touch) text.blur();
    scrollTo(0, 0);
    check({ text: message, image: screenshot?.data ?? null, image_type: screenshot?.type ?? null }, out);
  });
}

function reset() {
  running?.abort();
  running = null;
  busy = false;
  transition(() => {
    for (const img of report.querySelectorAll("img")) URL.revokeObjectURL(img.src);
    document.body.classList.add("empty");
    report.replaceChildren();
    newCheck.hidden = true;
    update();
    scrollTo(0, 0);
    if (!touch) text.focus();
  });
}

newCheck.addEventListener("click", () => (history.state?.check ? history.back() : reset()));
addEventListener("popstate", () => {
  if (!empty()) reset();
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!send.disabled) submit(text.value.trim(), image);
});

text.addEventListener("input", () => {
  update();
  fit();
});
text.addEventListener("keydown", (e) => {
  // On phones Enter adds a line; the send button sends.
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing && !touch) {
    e.preventDefault();
    form.requestSubmit();
  }
});
text.addEventListener("paste", (e) => {
  const file = [...e.clipboardData.files].find((f) => f.type.startsWith("image/"));
  if (file && !e.clipboardData.getData("text")) {
    e.preventDefault();
    attach(file);
  }
});

form.querySelector(".attach").addEventListener("click", () => picker.click());
picker.addEventListener("change", () => {
  if (picker.files[0]) attach(picker.files[0]);
  picker.value = "";
});
attachment.querySelector(".remove").addEventListener("click", () => {
  detach();
  text.focus();
});

addEventListener("dragover", (e) => {
  if (!e.dataTransfer.types.includes("Files")) return;
  e.preventDefault(); // otherwise the browser opens the dropped file
  if (empty()) form.classList.add("dragging");
  else e.dataTransfer.dropEffect = "none";
});
addEventListener("dragleave", (e) => {
  if (!e.relatedTarget) form.classList.remove("dragging");
});
addEventListener("drop", (e) => {
  e.preventDefault();
  form.classList.remove("dragging");
  if (empty() && e.dataTransfer.files[0]) attach(e.dataTransfer.files[0]);
});

for (const example of document.querySelectorAll(".examples button")) {
  example.addEventListener("click", () => submit(example.dataset.text, null));
}

update();
if (!touch) text.focus();
