document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    const senderId = window.SENDER_ID;
    const receiverId = window.RECEIVER_ID;
    const roomName = `chat_${Math.min(senderId, receiverId)}_${Math.max(senderId, receiverId)}`;

    socket.emit("join_room", { room: roomName });

    // Gửi thông báo đã đọc khi mở chat
    notifyRead(senderId, receiverId, roomName);

    socket.on("receive_message", (data) => {
        const { content, sender_id, sender_username, created_at, message_id, status } = data;
        const chatWindow = document.getElementById("chat-window") || document.getElementById("chat-box");
        if (!chatWindow) return;

        const wrapper = document.createElement("div");
        wrapper.className = "message";
        wrapper.dataset.id = message_id;

        const isOwnMessage = sender_id === senderId;

        // Nếu là tin mình gửi, căn phải
        if (isOwnMessage) {
            wrapper.style.textAlign = "right";
            wrapper.innerHTML = `
                <strong>${sender_username}:</strong> ${content}<br>
                <span class="meta">${created_at}</span><br>
                <span class="status" id="status-${message_id}" style="color: gray; font-style: italic;">
                    ${status}
                </span>
                <hr>
            `;
        } else {
            // Tin nhắn từ người khác
            wrapper.innerHTML = `
                <strong>${sender_username}:</strong> ${content}<br>
                <span class="meta">${created_at}</span>
                <hr>
            `;
        }

        chatWindow.appendChild(wrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });

    socket.on("messages_read", (data) => {
        const { read_message_ids } = data;
        read_message_ids.forEach(id => {
            const statusEl = document.querySelector(`#status-${id}`);
            if (statusEl) {
                statusEl.textContent = "Đã xem";
            }
        });
    });

    const form = document.getElementById("chat-form");
    form?.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = document.getElementById("message-input");
        const content = input.value.trim();
        if (!content) return;

        socket.emit("send_message", {
            sender_id: senderId,
            receiver_id: receiverId,
            content: content,
            room: roomName
        });

        input.value = "";
    });

    function notifyRead(sender_id, receiver_id, room) {
        socket.emit("read_messages", {
            sender_id: sender_id,
            receiver_id: receiver_id,
            room: room
        });
    }
});
