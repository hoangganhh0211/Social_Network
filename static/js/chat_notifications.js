const socket = io();

let newMessageCount = 0;
const badge = document.getElementById("message-badge");
const notifBar = document.getElementById("notification-bar");
const chatWindow = document.getElementById("chat-window");

function updateBadge(count) {
  if (count > 0) {
    badge.style.display = "inline-block";
    badge.innerText = count;
  } else {
    badge.style.display = "none";
  }
}

function showNotification(text) {
  notifBar.innerText = text;
  notifBar.style.display = "block";
  setTimeout(() => {
    notifBar.style.display = "none";
  }, 5000);
}

function isChatActive() {
  return chatWindow.classList.contains("active");
}

function resetNotifications() {
  newMessageCount = 0;
  updateBadge(newMessageCount);
  notifBar.style.display = "none";
}

notifBar.addEventListener("click", () => {
  chatWindow.classList.add("active");
  resetNotifications();
});

document.getElementById("open-chat-btn").addEventListener("click", () => {
  chatWindow.classList.add("active");
  resetNotifications();
});

socket.on("receive_message", (data) => {
  addMessageToChatWindow(data);

  if (!isChatActive()) {
    newMessageCount++;
    updateBadge(newMessageCount);
    showNotification(`Tin nhắn mới từ ${data.sender_username}: ${data.content}`);
  }
});

function addMessageToChatWindow(data) {
  const chat = document.getElementById("chat-window");
  const msgDiv = document.createElement("div");
  msgDiv.textContent = `${data.sender_username}: ${data.content}`;
  chat.appendChild(msgDiv);
  chat.scrollTop = chat.scrollHeight;
}
