const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let chatHistory = [];
let collectedData = {};

inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendButton.click();
  }
});

sendButton.addEventListener("click", async () => {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage("user", userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  inputField.value = "";

  const response = await fetch("http://localhost:8000/chat", {
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

  if (data.image_url) {
    appendImage(data.image_url);
  }
});

window.addEventListener("load", () => {
  const welcome = "Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh. Hôm nay quý khách muốn tạo thiết kế gì?";
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
  chatBox.appendChild(img);
  chatBox.scrollTop = chatBox.scrollHeight;
}
