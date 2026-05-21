from flask import Flask, render_template_string, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "gop_tat_ca_vao_mot_file_python_2026"

# 🗄️ KHỞI TẠO DATABASE (Sử dụng đường dẫn an toàn trên Render)
DB_PATH = os.path.join(os.getcwd(), 'diary_database.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT UNIQUE, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS diary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                        title TEXT, content TEXT, mood TEXT, is_public INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# 🎨 GIAO DIỆN HTML/JS TÍCH HỢP TAILWIND V3 SIÊU ỔN ĐỊNH
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoodDiary - Nhật Ký Online</title>
    <script src="https://tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 min-h-screen text-gray-800">

    <!-- 🔑 GIAO DIỆN ĐĂNG NHẬP -->
    <div id="loginPage" class="flex items-center justify-center min-h-screen p-4">
        <div class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md border border-purple-100">
            <div class="text-center mb-8">
                <span class="text-4xl">🔑</span>
                <h2 class="text-3xl font-extrabold text-gray-800 mt-2">Chào Quay Trở Lại</h2>
                <p class="text-gray-500 text-sm mt-1">Đăng nhập hệ thống Nhật ký Toàn cầu</p>
            </div>
            <form onsubmit="handleLogin(event)" class="space-y-5">
                <input type="text" id="loginUser" required placeholder="Tên tài khoản..." class="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400">
                <input type="password" id="loginPass" required placeholder="Mật khẩu..." class="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400">
                <button type="submit" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-xl font-bold hover:opacity-90 transition-all cursor-pointer">Đăng Nhập</button>
            </form>
            <p class="text-sm text-center text-gray-600 mt-6">Chưa có tài khoản? <button onclick="switchPage('registerPage')" class="text-purple-600 font-bold hover:underline cursor-pointer">Đăng ký mới</button></p>
        </div>
    </div>

    <!-- 📝 GIAO DIỆN ĐĂNG KÝ -->
    <div id="registerPage" class="hidden flex items-center justify-center min-h-screen p-4">
        <div class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md border border-purple-100">
            <div class="text-center mb-8">
                <span class="text-4xl">📝</span>
                <h2 class="text-3xl font-extrabold text-gray-800 mt-2">Tạo Tài Khoản</h2>
            </div>
            <form onsubmit="handleRegister(event)" class="space-y-5">
                <input type="text" id="regUser" required placeholder="Tên tài khoản mới..." class="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400">
                <input type="password" id="regPass" required placeholder="Mật khẩu..." class="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400">
                <button type="submit" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-xl font-bold hover:opacity-90 transition-all cursor-pointer">Đăng Ký Ngay</button>
            </form>
            <p class="text-sm text-center text-gray-600 mt-6">Đã có tài khoản? <button onclick="switchPage('loginPage')" class="text-purple-600 font-bold hover:underline cursor-pointer">Đăng nhập</button></p>
        </div>
    </div>

    <!-- 🔮 GIAO DIỆN CHÍNH (DASHBOARD) -->
    <div id="dashboardPage" class="hidden bg-slate-50 min-h-screen">
        <nav class="sticky top-0 z-50 bg-white shadow-sm border-b border-gray-100 px-6 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-2"><span class="text-2xl">🔮</span><span class="text-xl font-black text-purple-600">MoodDiary</span></div>
            <div class="flex items-center space-x-4">
                <p class="text-sm font-bold text-gray-800" id="displayUsername">@user</p>
                <button onclick="handleLogout()" class="bg-red-50 text-red-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-red-100 cursor-pointer">Đăng xuất</button>
            </div>
        </nav>

        <main class="max-w-7xl mx-auto mt-8 grid grid-cols-1 lg:grid-cols-4 gap-8 px-4 pb-12">
            <div class="lg:col-span-3 space-y-8">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 class="text-lg font-bold text-gray-800 mb-4">✍️ Hôm nay tâm trạng của bạn thế nào?</h3>
                    <form onsubmit="handleCabinetSubmit(event)" class="space-y-4">
                        <input type="text" id="diaryTitle" placeholder="Tiêu đề ngày hôm nay..." required class="w-full p-3 border border-gray-200 rounded-xl focus:outline-none">
                        <textarea id="diaryContent" rows="4" placeholder="Hãy viết ra những suy nghĩ của bạn..." required class="w-full p-3 border border-gray-200 rounded-xl focus:outline-none"></textarea>
                        <div class="flex flex-wrap items-center justify-between gap-4 pt-2">
                            <select id="diaryMood" class="p-2 border border-gray-200 rounded-xl bg-gray-50 font-medium text-sm">
                                <option>🚀 Tuyệt vời</option><option>🙂 Vui vẻ</option><option>😐 Bình thường</option><option>😢 Buồn bã</option><option>😡 Bực bội</option>
                            </select>
                            <div class="flex items-center space-x-6">
                                <label class="flex items-center space-x-2 text-sm text-gray-600 font-medium cursor-pointer">
                                    <input type="checkbox" id="diaryPublic" class="w-4 h-4 rounded text-purple-600">
                                    <span>Chia sẻ công khai với mọi người</span>
                                </label>
                                <button type="submit" class="bg-purple-600 text-white px-6 py-2.5 rounded-xl font-bold hover:bg-purple-700 cursor-pointer">Lưu Bài Viết</button>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="space-y-4">
                    <h3 class="text-xl font-extrabold text-gray-800">📅 Nhật ký & Bài chia sẻ từ cộng đồng</h3>
                    <div id="diaryList" class="space-y-4"></div>
                </div>
            </div>
            
            <div class="space-y-6">
                <div class="bg-gradient-to-br from-purple-600 to-indigo-600 p-6 rounded-2xl text-white shadow-xl">
                    <h4 class="font-bold text-lg mb-2">Trang web công cộng</h4>
                    <p class="text-xs opacity-85">Dự án đã kết nối internet toàn cầu thành công!</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        function switchPage(pageId) {
            document.getElementById('loginPage').style.display = pageId === 'loginPage' ? 'flex' : 'none';
            document.getElementById('registerPage').style.display = pageId === 'registerPage' ? 'flex' : 'none';
            document.getElementById('dashboardPage').style.display = pageId === 'dashboardPage' ? 'block' : 'none';
        }

        async function handleRegister(e) {
            e.preventDefault();
            const res = await fetch('/api/register', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: document.getElementById('regUser').value, password: document.getElementById('regPass').value})
            });
            const data = await res.json();
            alert(data.message);
            if (data.status === 'success') switchPage('loginPage');
        }

        async function handleLogin(e) {
            e.preventDefault();
            const res = await fetch('/api/login', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value})
            });
            const data = await res.json();
            if (data.status === 'success') {
                document.getElementById('displayUsername').innerText = "@" + data.username;
                switchPage('dashboardPage');
                loadDiaries();
            } else {
                alert(data.message);
            }
        }

        async function loadDiaries() {
            const res = await fetch('/api/diaries');
            const data = await res.json();
            const list = document.getElementById('diaryList');
            list.innerHTML = '';
            
            if (data.status === 'success') {
                if(data.diaries.length === 0){
                    list.innerHTML = '<p class="text-gray-500 italic text-center py-4">Chưa có bài viết nào. Hãy là người đầu tiên viết nhé!</p>';
                    return;
                }
                data.diaries.forEach(d => {
                    let border = 'border-l-gray-400';
                    if (d.mood.includes('🚀') || d.mood.includes('🙂')) border = 'border-l-green-500';
                    if (d.mood.includes('😢') || d.mood.includes('😡')) border = 'border-l-red-500';

                    list.innerHTML += `
                        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 border-l-4 ${border}">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-xl text-gray-800">${d.title}</h4>
                                    <p class="text-xs text-purple-600 mt-0.5">Tác giả: <b>${d.is_mine ? 'Bạn (Cá nhân)' : '@'+d.author}</b></p>
                                </div>
                                <span class="bg-purple-50 text-purple-700 text-xs px-3 py-1.5 rounded-full font-bold">${d.mood}</span>
                            </div>
                            <p class="text-gray-600 leading-relaxed">${d.content}</p>
                            <div class="mt-3 text-xs text-gray-400">${d.is_public ? '🌐 Đang chia sẻ công khai' : '🔒 Chỉ mình bạn thấy'}</div>
                        </div>`;
                });
            }
        }

        async function handleCabinetSubmit(e) {
            e.preventDefault();
            await fetch('/api/add_diary', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title: document.getElementById('diaryTitle').value,
                    content: document.getElementById('diaryContent').value,
                    mood: document.getElementById('diaryMood').value,
                    is_public: document.getElementById('diaryPublic').checked
                })
            });
            document.getElementById('diaryTitle').value = '';
            document.getElementById('diaryContent').value = '';
            loadDiaries();
        }

        async function handleLogout() {
            await fetch('/api/logout');
            switchPage('loginPage');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = generate_password_hash(data.get('password'))
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Đăng ký tài khoản thành công!"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Tên tài khoản này đã tồn tại!"})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect(DB_PATH)
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user, password):
        session['user_id'] = user
        session['username'] = user
        return jsonify({"status": "success", "username": user})
    return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu!"})

@app.route('/api/diaries', methods=['GET'])
def get_diaries():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Chưa đăng nhập"})
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT diary.title, diary.content, diary.mood, diary.is_public, users.username, 
        CASE WHEN diary.user_id = ? THEN 1 ELSE 0 END as is_mine
        FROM diary 
        JOIN users ON diary.user_id = users.id
        WHERE diary.user_id = ? OR diary.is_public = 1
        ORDER BY diary.id DESC
    """, (session['user_id'], session['user_id']))
    rows = cursor.fetchall()
    conn.close()
    diaries = [{"title": r, "content": r, "mood": r, "is_public": r, "author": r, "is_mine": r} for r in rows]
    return jsonify({"status": "success", "diaries": diaries})

@app.route('/api/add_diary', methods=['POST'])
def add_diary():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Chưa đăng nhập"})
    data = request.json
    is_public = 1 if data.get('is_public') else 0
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO diary (user_id, title, content, mood, is_public) VALUES (?, ?, ?, ?, ?)",
                 (session['user_id'], data.get('title'), data.get('content'), data.get('mood'), is_public))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/logout')
def api_logout():
    session.clear()
    return jsonify({"status": "success"})

# THAY ĐỔI CỔNG MẠNG ĐỂ CHẠY ĐƯỢC TRÊN RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
