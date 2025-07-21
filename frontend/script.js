const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const designInfoBox = document.getElementById("design-info");

let chatHistory = [];
let collectedData = {};
const sessionId = crypto.randomUUID();
const BASE_URL = window.location.origin;

// Gửi khi Enter (trừ Shift)
inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendButton.click();
  }
});

// Auto height textarea
inputField.addEventListener("input", () => {
  inputField.style.height = "auto";
  inputField.style.height = inputField.scrollHeight + "px";
});

// Gửi tin nhắn
sendButton.addEventListener("click", async () => {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage("user", userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  inputField.value = "";
  inputField.style.height = "38px";

  try {
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

    if (data.image_url) {
      appendImage(data.image_url);
    }

    await fetchDesignDataAndUpdateSidebar();

  } catch (error) {
    console.error("Lỗi khi gọi API:", error);
    appendMessage("assistant", "❌ Có lỗi xảy ra khi kết nối đến máy chủ.");
  }
});

// Tin nhắn chào + fetch design_data ban đầu
window.addEventListener("load", async () => {
  const welcome = `
Xin chào quý khách! Tôi là trợ lý thiết kế ảo thông minh, nhiệm vụ của tôi là ghi nhận và giúp đỡ thiết kế ý tưởng cho quý khách.

**-- Khả năng của tôi --**

Tôi có khả năng làm được những việc như sau:
- Tôi có thể thu thập thông tin về ý tưởng thiết kế mong muốn của quý khách
- Tôi sẽ tạo ra vài ý tưởng thiết kế và demo nếu như quý khách yêu cầu trực tiếp và có đủ các thông tin thiết yếu

**-- Lưu ý khi sử dụng --**

Để có thể có được trải nghiệm tốt nhất, xin quý khách vui lòng tuân thủ theo các ý sau:
- Câu từ rõ nghĩa và dễ hiểu
- Hãy cung cấp đầy đủ thông tin cần thiết trước khi yêu cầu tạo ý tưởng hay tạo demo
- Yêu cầu càng chi tiết thì độ chính xác càng cao
- Tôi chỉ có thể giúp lên ý tưởng tạm thời, để có được sản phẩm chuyên nghiệp và hoàn chỉnh, xin vui lòng liên hệ lại với nhân viên chính thức trong công ty

Cảm ơn quý khách đã tin tưởng và sử dụng dịch vụ của công ty chúng tôi.
Để bắt đầu, xin hãy gửi yêu cầu của quý khách để tôi có thể giúp đỡ ạ.
  `;
  appendMessage("assistant", welcome);
  chatHistory.push({ role: "assistant", content: welcome });

  await fetchDesignDataAndUpdateSidebar();
});

// Hiển thị tin nhắn
function appendMessage(role, text) {
  const msg = document.createElement("div");
  msg.className = role === "user" ? "user-msg" : "bot-msg";

  if (role === "assistant") {
    msg.innerHTML = marked.parse(text);

    // ✅ Gắn target="_blank" cho tất cả link
    const links = msg.querySelectorAll("a");
    links.forEach(link => {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    });

  } else {
    msg.innerHTML = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Hiển thị ảnh
function appendImage(url) {
  const img = document.createElement("img");
  img.src = url;
  img.alt = "Generated Image";
  img.className = "generated-image";
  img.style.marginTop = "10px";
  chatBox.appendChild(img);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ✅ Cập nhật lại thông tin bên phải
async function fetchDesignDataAndUpdateSidebar() {
  try {
    const response = await fetch(`${BASE_URL}/design_data/${sessionId}`);
    const result = await response.json();

    if (result && typeof result === "object") {
      collectedData = result;
      updateDesignInfoBox(result);
    }
  } catch (err) {
    console.error("❌ Không thể lấy thông tin thiết kế:", err);
  }
}

// ✅ Render card UI thay cho JSON thô
function updateDesignInfoBox(data) {
  try {
    let html = "";

    for (const [key, value] of Object.entries(data)) {
      const readableKey = convertKeyToLabel(key);
      const readableValue = Array.isArray(value) ? value.join(", ") : value;

      html += `
        <div class="info-card">
          <h3>${readableKey}</h3>
          <p>${readableValue}</p>
        </div>
      `;
    }

    designInfoBox.innerHTML = html || "<p>Chưa có thông tin nào được ghi nhận.</p>";
  } catch {
    designInfoBox.innerHTML = "<p>Không thể hiển thị dữ liệu.</p>";
  }
}

// ✅ Mapping key kỹ thuật sang nhãn tiếng Việt
function convertKeyToLabel(key) {
  const map = {
    product: "Sản phẩm thiết kế",
    color: "Màu sắc",
    style: "Phong cách",
    notes: "Ghi chú thêm",
    company: "Doanh nghiệp (nếu có)",
    selected_concept: "Ý tưởng đã chọn",
    // Thêm các field khác nếu cần
  };
  return map[key] || key;
}

// Toggle menu bên trái (mobile)
document.getElementById("toggle-left").addEventListener("click", () => {
  document.getElementById("sidebar-left").classList.toggle("active");
});

// Toggle menu bên phải (mobile)
const infoToggleButton = document.getElementById("toggle-right");
if (infoToggleButton) {
  infoToggleButton.addEventListener("click", () => {
    document.querySelector(".sidebar-right").classList.toggle("active");
  });
}
