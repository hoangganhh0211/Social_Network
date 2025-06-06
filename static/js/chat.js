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

        if (isOwnMessage) {
            // Tin mình gửi — căn phải, giữ trạng thái "Đã gửi"
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
            // Ngay khi nhận được tin nhắn là của bạn (receiver), bắn event messages_read để server đánh dấu đã đọc
            notifyRead(sender_id, receiverId, roomName);
        }

        chatWindow.appendChild(wrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });


    // Cập nhật trạng thái tin nhắn đã đọc
    socket.on("messages_read", (data) => {
        const { read_message_ids } = data;
        read_message_ids.forEach(id => {
            const statusEl = document.querySelector(`#status-${id}`);
            if (statusEl) {
                statusEl.textContent = "Đã xem";
            }
        });
    });

    // Xử lý gửi tin nhắn
    const form = document.getElementById("chat-form");
    form?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("message-input");
        const content = input.value.trim();
        if (!content) return;

        // 1. Gửi qua socket 
        socket.emit("send_message", {
            sender_id: senderId,
            receiver_id: receiverId,
            content: content,
            room: roomName
        });

        // 2. Đồng thời gửi POST để Flask lưu Message & Notification
        const formData = new FormData();
        formData.append("receiver_id", receiverId);
        formData.append("content", content);
        try {
            await fetch("/messages/send", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
        });
        } catch (err) {
        console.error("Không thể lưu notification:", err);
        }

        input.value = "";
    });

    // Gửi thông báo đã đọc khi người dùng mở chat
    function notifyRead(sender_id, receiver_id, room) {
        socket.emit("messages_read", {
            sender_id: sender_id,
            receiver_id: receiver_id,
            room: room
        });
    }
});
