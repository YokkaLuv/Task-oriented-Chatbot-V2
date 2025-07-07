const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let chatHistory = [];
let collectedData = {};

// ✅ Luôn tạo session ID mới khi load trang
const sessionId = crypto.randomUUID();

const BASE_URL = window.location.origin;

// Gửi tin nhắn khi Enter
inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendButton.click();
});

// Gửi khi bấm nút
sendButton.addEventListener("click", async () => {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage("user", userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  inputField.value = "";

  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: userMessage,
      history: chatHistory,
      design_data: collectedData
    })
  });

  const data = await response.json();

  const assistantReply = data.reply || "Xin lỗi, tôi chưa xử lý được yêu cầu.";
  chatHistory.push({ role: "assistant", content: assistantReply });
  appendMessage("assistant", assistantReply);

  if (data.design_data) {
    collectedData = { ...collectedData, ...data.design_data };
  }

  if (data.image_url) {
    appendImage(data.image_url);
  }
});

window.addEventListener("load", () => {
  const welcome =
    "Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh, tôi sẽ giúp đỡ thiết kế ý tưởng cho quý khách. Xin hãy gửi thông tin bất kỳ để bắt đầu ạ.";
  appendMessage("assistant", welcome);
  chatHistory.push({ role: "assistant", content: welcome });
});

function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";

  if (role === "assistant") {
    msg.innerHTML = marked.parse(text);  // ✅ Hỗ trợ markdown cho assistant
  } else {
    msg.textContent = text;
  }

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
