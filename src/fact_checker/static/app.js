const form = document.querySelector(".composer");
const text = form.elements.text;
const send = form.querySelector(".send");
const picker = form.querySelector("input[type=file]");
const attachment = form.querySelector(".attachment");
const problem = document.querySelector(".problem");
const messages = document.querySelector(".messages");
const icons = document.querySelector("#verdict-icons").content;

const IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const LABELS = { true: "True", false: "False", misleading: "Misleading", unverifiable: "Unverified" };
const touch = matchMedia("(pointer: coarse)").matches;

let image = null; // { data: base64, type, url }
let busy = false;
let following = true; // keep the newest output in view unless the reader scrolled up

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

const icon = (selector) => icons.querySelector(selector).cloneNode(true);
const host = (url) => new URL(url).hostname.replace(/^www\./, "");

function update() {
  send.disabled = busy || !(text.value.trim() || image);
  text.style.height = "auto";
  text.style.height = `${text.scrollHeight}px`;
}

function say(message) {
  problem.textContent = message;
  problem.hidden = !message;
}

function scrollDown() {
  if (following) scrollTo(0, document.documentElement.scrollHeight);
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
  const parts = [el("p", { className: "reply" }, ...linkify(reply)), copy];
  if (results.length) parts.push(el("ul", { className: "claims" }, ...results.map(claim)));
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

function fail(li, message, payload) {
  li.removeAttribute("aria-busy");
  li.replaceChildren(el("p", { className: "failed", textContent: message }));
  if (payload) {
    li.append(el("button", { type: "button", className: "retry", textContent: "Try again", onclick: () => check(payload, li) }));
  }
}

async function check(payload, li) {
  if (busy) return;
  busy = true;
  update();
  const label = el("span", { textContent: "Reading the message…" });
  const steps = el("ol");
  const progress = el("details", { className: "progress" }, el("summary", {}, label, icon('[data-icon="chevron"]')), steps);
  progress.dataset.running = "";
  li.setAttribute("aria-busy", "true");
  li.replaceChildren(progress);
  following = true;
  scrollDown();
  const started = Date.now();
  try {
    const response = await fetch("/api/checks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.status === 429) return fail(li, "You've reached today's limit. Please try again tomorrow.");
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
        li.append(...answer(event));
        li.removeAttribute("aria-busy");
        done = true;
      }
      scrollDown();
    }
    if (!done) throw new Error("Stream ended early");
  } catch {
    fail(li, "Something went wrong. Please try again.", payload);
  } finally {
    busy = false;
    update();
    scrollDown();
  }
}

function submit(forward, screenshot) {
  const show = () => {
    document.body.classList.remove("empty");
    const bubble = el("li", { className: "user" });
    if (screenshot) bubble.append(el("img", { src: screenshot.url, alt: "Screenshot sent for checking" }));
    if (forward) bubble.append(el("p", { textContent: forward }));
    messages.append(bubble);
    text.value = "";
    detach();
    say("");
    if (touch) text.blur();
    check({ text: forward, image: screenshot?.data ?? null, image_type: screenshot?.type ?? null },
      messages.appendChild(el("li", { className: "assistant" })));
  };
  if (document.body.classList.contains("empty") && document.startViewTransition) document.startViewTransition(show);
  else show();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!send.disabled) submit(text.value.trim(), image);
});

text.addEventListener("input", update);
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
  e.preventDefault();
  form.classList.add("dragging");
});
addEventListener("dragleave", (e) => {
  if (!e.relatedTarget) form.classList.remove("dragging");
});
addEventListener("drop", (e) => {
  e.preventDefault();
  form.classList.remove("dragging");
  if (e.dataTransfer.files[0]) attach(e.dataTransfer.files[0]);
});

addEventListener("scroll", () => {
  following = innerHeight + scrollY >= document.documentElement.scrollHeight - 120;
});

for (const example of document.querySelectorAll(".examples button")) {
  example.addEventListener("click", () => {
    if (!busy) submit(example.dataset.text, null);
  });
}

update();
if (!touch) text.focus();
