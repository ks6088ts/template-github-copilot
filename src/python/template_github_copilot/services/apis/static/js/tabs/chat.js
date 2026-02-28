/**
 * chat.js – Chat tab module.
 *
 * Registers itself with App.registerTab("chat", ...).
 */
(() => {
  const chatContainer = document.getElementById("chat-container");
  const chatEmpty = document.getElementById("chat-empty");
  const inputBar = document.getElementById("input-bar");
  const msgInput = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");

  // ── Message helpers ───────────────────────────────────────────
  function appendMessage(text, cls) {
    if (chatEmpty && chatEmpty.parentNode) chatEmpty.remove();
    const displayText = cls.includes("bot") ? text.trim() : text;
    if (cls.includes("bot")) {
      const wrapper = document.createElement("div");
      wrapper.className = "msg-wrapper";
      const div = document.createElement("div");
      div.className = `message ${cls}`;
      div.textContent = displayText;
      wrapper.appendChild(div);
      wrapper.appendChild(App.createCopyBtn(() => div.textContent));
      chatContainer.appendChild(wrapper);
      chatContainer.scrollTop = chatContainer.scrollHeight;
      return div;
    }
    const div = document.createElement("div");
    div.className = `message ${cls}`;
    div.textContent = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return div;
  }

  async function sendMessage() {
    const text = msgInput.value.trim();
    if (!text) return;
    msgInput.value = "";
    appendMessage(text, "user");

    const typing = document.createElement("div");
    typing.className = "typing";
    typing.innerHTML = '<span class="typing-dots"><span></span><span></span><span></span></span> Thinking…';
    chatContainer.appendChild(typing);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    sendBtn.disabled = true;
    msgInput.disabled = true;

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      typing.remove();
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        appendMessage(`Error: ${err.detail || resp.statusText}`, "bot error");
        return;
      }
      const data = await resp.json();
      appendMessage(data.reply, "bot");
    } catch (e) {
      typing.remove();
      appendMessage(`Network error: ${e.message}`, "bot error");
    } finally {
      sendBtn.disabled = false;
      msgInput.disabled = false;
      msgInput.focus();
    }
  }

  // ── Tab registration ──────────────────────────────────────────
  App.registerTab("chat", "Chat", {
    init() {
      sendBtn.addEventListener("click", sendMessage);
      msgInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    },
    show() {
      chatContainer.style.display = "flex";
      inputBar.style.display = "flex";
      msgInput.focus();
    },
    hide() {
      chatContainer.style.display = "none";
      inputBar.style.display = "none";
    },
  });
})();
