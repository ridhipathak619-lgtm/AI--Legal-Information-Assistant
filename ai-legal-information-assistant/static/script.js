const thread = document.getElementById("thread");
const form = document.getElementById("composer");
const input = document.getElementById("msg");
const send = document.getElementById("send");

function add(html) {
  document.getElementById("empty")?.remove();
  thread.insertAdjacentHTML("beforeend", html);
  window.scrollTo(0, document.body.scrollHeight);
}
const esc = s => s.replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));

async function ask(text) {
  add(`<div class="q">${esc(text)}</div>`);
  add(`<div class="a" id="pending"><div class="text">Searching the documents…</div><div class="src"></div></div>`);
  const pending = document.getElementById("pending");
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed.");
    const list = data.sources.map(s => `<li>${esc(s)}</li>`).join("");
    pending.querySelector(".text").textContent = data.answer;
    pending.querySelector(".src").innerHTML = list ? `<strong>Sources</strong><ul>${list}</ul>` : "";
  } catch (e) {
    pending.classList.add("err");
    pending.querySelector(".text").textContent = e.message;
  }
  pending.removeAttribute("id");
}

form.addEventListener("submit", async e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  send.disabled = true;
  await ask(text);
  send.disabled = false;
  input.focus();
});
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
});
