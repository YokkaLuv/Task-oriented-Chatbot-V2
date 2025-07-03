const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let chatHistory = [];
let collectedData = {};
let conceptButtonGroup = null;

// Tạo session_id cố định cho user
let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("session_id", sessionId);
}

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

  if (data.concepts) {
    showConceptButtons(data.concepts);
  }
});

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

      // Disable all buttons
      const allBtns = conceptButtonGroup.querySelectorAll("button");
      allBtns.forEach((b) => {
        b.disabled = true;
        b.style.cursor = "not-allowed";
        b.style.opacity = "0.6";
      });

      const choiceText = `Tôi chọn ý tưởng ${index + 1}`;
      appendMessage("user", choiceText);
      chatHistory.push({ role: "user", content: choiceText });

      const response = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          selected_concept: conceptText,
          message: "",
          history: chatHistory,
          design_data: collectedData
        })
      });

      const data = await response.json();

      const reply = data.reply || "Đây là hình ảnh demo dựa trên concept bạn đã chọn.";
      chatHistory.push({ role: "assistant", content: reply });
      appendMessage("assistant", reply);

      if (data.image_url) {
        appendImage(data.image_url);
      }
    });

    conceptButtonGroup.appendChild(btn);
  });

  chatBox.appendChild(conceptButtonGroup);
  chatBox.scrollTop = chatBox.scrollHeight;
}

window.addEventListener("load", () => {
  const welcome =
    "Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh, tôi sẽ giúp đỡ thiết kế ý tưởng cho quý khách. Xin hãy gửi tin nhắn bất kỳ để bắt đầu ạ.";
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
