const form = document.querySelector(".composer");
const text = form.elements.text;
const send = form.querySelector(".send");
const picker = form.querySelector("input[type=file]");
const attachment = form.querySelector(".attachment");
const problem = document.querySelector(".problem");
const report = document.querySelector(".report");
const newCheck = document.querySelector(".new-check");
const note = document.querySelector(".note");
const panel = document.querySelector(".history");
const list = panel.querySelector("ul");
const icons = document.querySelector("#verdict-icons").content;

const IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const LABELS = { true: "True", false: "False", misleading: "Misleading", unverifiable: "Unverified" };
const ERRORS = { failed: "Something went wrong.", limit: "You've reached today's limit. Please try again tomorrow." };
const KEEP = 20; // checks kept in history
const touch = matchMedia("(pointer: coarse)").matches;

let image = null; // { file, url }
let busy = false;
let running = null; // AbortController of the check streaming in
// A check: { id, at, text, image: Blob | null, steps, then reply, results, seconds or error }. Newest first.
let records = [];
let current = null; // the record on the page
const following = new Set();

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

const icon = (selector) => icons.querySelector(selector).cloneNode(true);
const host = (url) => new URL(url).hostname.replace(/^www\./, "");
const empty = () => document.body.classList.contains("empty");
const transition = (change) => (document.startViewTransition ? document.startViewTransition(change) : change());
const pending = (record) => !("reply" in record || record.error);
const title = (record) => record.text.trim().split("\n")[0] || record.results?.[0]?.claim || "Screenshot";

const base64 = (blob) => new Promise((resolve) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result.split(",")[1]);
  reader.readAsDataURL(blob);
});

// History lives in this browser only. Without IndexedDB (some private modes) it lasts until the tab closes.
const db = new Promise((resolve, reject) => {
  const open = indexedDB.open("fact-checker", 1);
  open.onupgradeneeded = () => open.result.createObjectStore("checks", { keyPath: "id" });
  open.onsuccess = () => resolve(open.result);
  open.onerror = () => reject(open.error);
});

async function store(method, ...args) {
  try {
    const request = (await db).transaction("checks", "readwrite").objectStore("checks")[method](...args);
    return await new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  } catch {
    return undefined;
  }
}

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

function attach(file) {
  if (!IMAGE_TYPES.includes(file.type)) return say("Screenshots must be PNG, JPG or WebP.");
  if (file.size > MAX_IMAGE_BYTES) return say("Screenshots must be under 5 MB.");
  detach();
  image = { file, url: URL.createObjectURL(file) };
  attachment.prepend(el("img", { src: image.url, alt: "Screenshot to check" }));
  attachment.hidden = false;
  say("");
  update();
}

function detach() {
  if (image) URL.revokeObjectURL(image.url);
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

const links = (result) => result.sources.filter((s) => /^https?:\/\//.test(s.url));

// What "Copy reply" puts on the clipboard: plain text that reads well pasted into any chat.
function transcript(reply, results) {
  const claims = results.map((r) => [`${LABELS[r.verdict]}: ${r.claim}`, r.rationale, ...links(r).map((s) => s.url)]);
  return [reply, ...claims.map((lines) => lines.join("\n"))].join("\n\n");
}

function claim(result) {
  const badge = el("span", { className: "badge" }, icon(`[data-verdict="${result.verdict}"]`), LABELS[result.verdict]);
  badge.dataset.verdict = result.verdict;
  const sources = links(result)
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
      await navigator.clipboard.writeText(transcript(reply, results));
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
  if (results.length) parts.push(el("ul", { className: "claims" }, ...results.map(claim)), copy);
  return parts;
}

// The result area of the check on the page, drawn from its record: progress, then the result or what went wrong.
function show(record) {
  const out = report.querySelector(".result");
  note.hidden = true;
  if (record.error) {
    out.removeAttribute("aria-busy");
    out.replaceChildren(el("p", { className: "failed", textContent: ERRORS[record.error] }));
    if (record.error === "failed") {
      const again = () => retry(record);
      out.append(el("button", { type: "button", className: "retry", textContent: "Try again", onclick: again }));
    }
  } else {
    const done = !pending(record);
    const label = done ? `Checked in ${record.seconds}s` : `${record.steps.at(-1) ?? "Reading the message"}…`;
    const progress = el("details", { className: "progress", open: !!out.querySelector(".progress")?.open },
      el("summary", {}, el("span", { textContent: label }), icon('[data-icon="chevron"]')),
      el("ol", {}, ...record.steps.map((step) => el("li", { textContent: step }))));
    progress.toggleAttribute("data-running", !done);
    if (done) out.removeAttribute("aria-busy");
    else out.setAttribute("aria-busy", "true");
    out.replaceChildren(progress, ...(done ? answer(record) : []));
  }
  if (!pending(record) && newCheck.hidden) transition(() => (newCheck.hidden = false));
}

function draw() {
  list.replaceChildren(...records.map((record) => {
    const open = el("button", {
      type: "button", className: "open", textContent: title(record), onclick: () => visit(record),
    });
    if (record === current) open.setAttribute("aria-current", "page");
    open.toggleAttribute("data-running", pending(record));
    const forget = el("button", {
      type: "button", className: "forget", ariaLabel: `Delete “${title(record)}”`, onclick: () => remove(record),
    }, icon('[data-verdict="false"]'));
    return el("li", {}, open, forget);
  }));
}

// Keeps a record: in history once it has an id, the newest KEEP of them, and on the page if it is the one shown.
function save(record) {
  if (record.id) {
    const added = !records.includes(record);
    if (added) {
      records.unshift(record);
      for (const old of records.splice(KEEP)) store("delete", old.id);
    }
    store("put", record);
    if (added || !pending(record)) draw(); // not per step: a redraw under the pointer loses the click
  }
  if (record === current) show(record);
}

function remove(record) {
  records = records.filter((r) => r !== record);
  store("delete", record.id);
  if (record === current) startOver();
  else draw();
}

// A check that lost its stream still runs on the server: ask for its outcome until it has one.
async function follow(record) {
  if (following.has(record)) return;
  following.add(record);
  while (records.includes(record) && pending(record)) {
    await new Promise((resolve) => setTimeout(resolve, 3000));
    const outcome = await fetch(`/api/checks/${record.id}`).then((r) => r.json()).catch(() => ({}));
    if (records.includes(record) && ("reply" in outcome || outcome.error)) save(Object.assign(record, outcome));
  }
  following.delete(record);
}

async function check(record) {
  const controller = (running = new AbortController());
  busy = true;
  newCheck.hidden = true;
  update();
  save(record);
  try {
    const response = await fetch("/api/checks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: record.text,
        image: record.image && (await base64(record.image)),
        image_type: record.image?.type ?? null,
      }),
      signal: controller.signal,
    });
    if (response.status === 429) return save(Object.assign(record, { error: "limit" }));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    for await (const event of lines(response.body)) {
      if (event.id) history.replaceState({ id: event.id }, "");
      if (!event.step) Object.assign(record, event);
      else if (!record.steps.includes(event.step)) record.steps.push(event.step);
      save(record);
    }
    if (pending(record)) throw new Error("Stream ended early");
  } catch {
    if (record.id) follow(record);
    else if (!controller.signal.aborted) save(Object.assign(record, { error: "failed" }));
  } finally {
    // A check the reader left must not touch the page that replaced it.
    if (running === controller) {
      running = null;
      busy = false;
      update();
    }
  }
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

// A check replaces the page: the message on the right, then its result. A running check on the page runs on.
function display(record) {
  running?.abort();
  running = null;
  busy = false;
  current = record;
  for (const img of report.querySelectorAll("img")) URL.revokeObjectURL(img.src);
  document.body.classList.remove("empty");
  const quote = el("blockquote", { className: "message" });
  if (record.image) {
    quote.append(el("img", { src: URL.createObjectURL(record.image), alt: "Screenshot sent for checking" }));
  }
  if (record.text) quote.append(el("p", { textContent: record.text }));
  report.replaceChildren(quote, el("div", { className: "result" }));
  fold(quote);
  newCheck.hidden = pending(record);
  show(record);
  draw();
  update();
  scrollTo(0, 0);
  if (panel.matches(":popover-open")) panel.hidePopover();
}

// A new check of the same message takes the failed one's place.
function retry(record) {
  const again = { text: record.text, image: record.image, steps: [], at: Date.now() };
  transition(() => {
    display(again);
    remove(record);
    check(again);
  });
}

// Each check gets its own history entry, so Back and Forward move between checks and the empty page.
function submit(message, screenshot) {
  if (busy) return;
  busy = true; // now, not in the transition: a held Enter must not start a second check
  update();
  history.pushState({}, "");
  const record = { text: message, image: screenshot?.file ?? null, steps: [], at: Date.now() };
  transition(() => {
    display(record);
    text.value = "";
    text.style.height = ""; // back to one row
    detach();
    say("");
    if (touch) text.blur();
    check(record);
  });
}

function visit(record) {
  if (record !== current) {
    history.pushState({ id: record.id }, "");
    transition(() => display(record));
  } else if (panel.matches(":popover-open")) panel.hidePopover();
}

function reset() {
  running?.abort();
  running = null;
  busy = false;
  current = null;
  transition(() => {
    for (const img of report.querySelectorAll("img")) URL.revokeObjectURL(img.src);
    document.body.classList.add("empty");
    report.replaceChildren();
    newCheck.hidden = true;
    draw();
    update();
    scrollTo(0, 0);
    if (!touch) text.focus();
  });
}

function startOver() {
  history.pushState({}, "");
  reset();
}

// Wide screens collapse the panel, remembered per browser; narrow ones open it as a drawer (the toggle's popovertarget).
const toggle = document.querySelector(".history-toggle");
const wide = matchMedia("(min-width: 64rem)");
function collapse(collapsed) {
  document.body.classList.toggle("collapsed", collapsed);
  if (wide.matches) toggle.setAttribute("aria-expanded", String(!collapsed));
  else toggle.removeAttribute("aria-expanded"); // the popover reports its own state
}
toggle.addEventListener("click", (e) => {
  if (!wide.matches) return;
  e.preventDefault(); // no popover here
  const collapsed = !document.body.classList.contains("collapsed");
  collapse(collapsed);
  try {
    localStorage.setItem("collapsed", collapsed ? "1" : "");
  } catch {}
});
wide.addEventListener("change", () => collapse(document.body.classList.contains("collapsed")));
try {
  collapse(!!localStorage.getItem("collapsed"));
} catch {}

newCheck.addEventListener("click", startOver);
addEventListener("popstate", () => {
  const record = records.find((r) => r.id === history.state?.id);
  if (record) transition(() => display(record));
  else if (!empty()) reset();
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

// A reload returns to the check it was on; checks still running when the page last closed are picked up.
store("getAll").then((all = []) => {
  records = all.sort((a, b) => b.at - a.at);
  draw();
  document.body.offsetWidth; // lay out the filled list first, so only later changes slide
  document.body.classList.add("ready");
  records.filter(pending).forEach(follow);
  const record = records.find((r) => r.id === history.state?.id);
  if (record) display(record);
});
