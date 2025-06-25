const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let chatHistory = [];
let collectedData = {};
let userMessageCount = 0;
let conceptButtonGroup = null;

const BASE_URL = window.location.origin;

inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendButton.click();
  }
});

sendButton.addEventListener("click", async () => {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  userMessageCount++;
  appendMessage("user", userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  inputField.value = "";

  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: userMessage,
      history: chatHistory,
      design_data: collectedData
    })
  });

  const data = await response.json();
  const assistantReply = data.reply;
  chatHistory.push({ role: "assistant", content: assistantReply });
  appendMessage("assistant", assistantReply);

  if (userMessageCount >= 7) {
    insertConceptButtonBelowLastMessage();
  }

  if (data.image_url) {
    appendImage(data.image_url);
  }
});

function insertConceptButtonBelowLastMessage() {
  const btn = document.createElement("button");
  btn.textContent = "✨ Xây dựng ý tưởng ✨";
  btn.className = "concept-btn";
  btn.style.margin = "10px 0";

  btn.addEventListener("click", async () => {
    const transcript = chatHistory.map(m => `${m.role}: ${m.content}`).join("\n");

    const response = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        generate_concepts: true,
        transcript: transcript
      })
    });

    const data = await response.json();
    const concepts = data.concepts;
    showConceptButtons(concepts);
  });

  chatBox.appendChild(btn);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showConceptButtons(concepts) {
  if (conceptButtonGroup) conceptButtonGroup.remove();

  conceptButtonGroup = document.createElement("div");
  conceptButtonGroup.className = "concept-group";

  concepts.forEach((conceptText, index) => {
    const btn = document.createElement("button");
    btn.textContent = conceptText;
    btn.className = "concept-choice-btn";
    btn.style.margin = "5px 0";

    btn.addEventListener("click", async () => {
      btn.classList.add("selected-concept");

      const allBtns = conceptButtonGroup.querySelectorAll("button");
      allBtns.forEach(b => {
        b.disabled = true;
        b.style.cursor = "not-allowed";
        b.style.opacity = "0.6";
      });

      appendMessage("user", `Tôi chọn ý tưởng ${index + 1}`);
      chatHistory.push({ role: "user", content: `Tôi chọn ý tưởng ${index + 1}` });

      const response = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          generate_image: true,
          concept: conceptText
        })
      });

      const data = await response.json();
      if (data.image_url) {
        appendMessage("assistant", "Đây là hình ảnh demo về ý tưởng mà quý khách đã chọn, cảm ơn quý khách đã sử dụng dịch vụ của chúng tôi.");
        appendImage(data.image_url);
      }
    });

    conceptButtonGroup.appendChild(btn);
  });

  chatBox.appendChild(conceptButtonGroup);
  chatBox.scrollTop = chatBox.scrollHeight;
}

window.addEventListener("load", () => {
  const welcome = "Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh, tôi sẽ giúp đỡ thiết kế ý tưởng cho quý khách. Xin hãy gửi tin nhắn bất kì để bắt đầu ạ.";
  appendMessage("assistant", welcome);
  chatHistory.push({ role: "assistant", content: welcome });
});

function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function appendImage(url) {
  const img = document.createElement("img");
  img.src = url;
  img.alt = "Generated Image";
  img.className = "generated-image";
  img.style.marginTop = "10px";
  chatBox.appendChild(img);
  chatBox.scrollTop = chatBox.scrollHeight;
}
