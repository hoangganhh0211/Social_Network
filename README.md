# Social_Network
Trang web mạng xã hội 
Xây dựng một trang web mạng xã hội mini cho phép người dùng có thể đăng bài, chơi game, kết bạn, nhắn tin với nhau.

git add .
git commit -m "Update url cho phần notification trỏ đúng thông báo"
git push origin main

flask db migrate -m "Sửa lại Notification"
flask db upgrade