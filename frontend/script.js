const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let chatHistory = [];
let collectedData = {};

// ✅ Luôn tạo session ID mới khi load trang
const sessionId = crypto.randomUUID();
const BASE_URL = window.location.origin;

// ✅ Gửi tin nhắn khi Enter (trừ khi giữ Shift để xuống dòng)
inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault(); // Ngăn xuống dòng mặc định
    sendButton.click();
  }
});

// ✅ Tự động co giãn chiều cao textarea
inputField.addEventListener("input", () => {
  inputField.style.height = "auto";
  inputField.style.height = inputField.scrollHeight + "px";
});

// ✅ Gửi tin nhắn khi bấm nút
sendButton.addEventListener("click", async () => {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage("user", userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  inputField.value = "";
  inputField.style.height = "38px"; // reset chiều cao

  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: userMessage,
      history: chatHistory,
      design_data: collectedData,
    }),
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

// ✅ Tin nhắn chào khi mở trang
window.addEventListener("load", () => {
  const welcome =
    "Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh, tôi sẽ giúp đỡ thiết kế ý tưởng cho quý khách. Xin hãy gửi thông tin bất kỳ để bắt đầu ạ.";
  appendMessage("assistant", welcome);
  chatHistory.push({ role: "assistant", content: welcome });
});

// ✅ Hiển thị tin nhắn
function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";

  if (role === "assistant") {
    msg.innerHTML = marked.parse(text); // hỗ trợ markdown
  } else {
    // giữ xuống dòng và escape HTML cơ bản
    msg.innerHTML = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ✅ Hiển thị ảnh
function appendImage(url) {
  const img = document.createElement("img");
  img.src = url;
  img.alt = "Generated Image";
  img.className = "generated-image";
  img.style.marginTop = "10px";
  chatBox.appendChild(img);
  chatBox.scrollTop = chatBox.scrollHeight;
}
