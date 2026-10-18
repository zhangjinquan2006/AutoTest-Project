from flask import Flask, request, render_template_string
import pymysql

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',  # 改密码
        database='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 1. 注册页面（浏览器打开就能填）
@app.route('/')
def index():
    return render_template_string('''
        <h2>用户注册</h2>
        <form action="/register" method="POST">
            账号：<input type="text" name="username"><br><br>
            密码：<input type="password" name="password"><br><br>
            <button type="submit">注册</button>
        </form>
    ''')

# 2. 处理注册（把数据写入数据库）
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return f"<h1>注册成功！{username}，请去登录</h1><a href='/'>返回</a>"
    except Exception as e:
        return f"<h1>注册失败：{e}</h1><a href='/'>返回</a>"
    finally:
        cursor.close()
        conn.close()


from flask import Flask, request, jsonify  # 确保导入了 jsonify


# ========== 登录接口改造：返回 Token ==========
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        # 登录成功，返回一个 Token（这里简单用用户名当 Token 演示）
        token = f"token_{username}"
        return jsonify({"msg": "登录成功", "token": token}), 200
    else:
        return jsonify({"msg": "登录失败"}), 401


# ========== 需要鉴权的接口 ==========
@app.route('/api/user_info', methods=['GET'])
def api_user_info():
    # 从请求头里取 Token
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"msg": "未提供 Token，拒绝访问"}), 401

    token = auth_header.replace('Bearer ', '')

    # 简单校验：Token 是不是以 "token_" 开头
    if not token.startswith('token_'):
        return jsonify({"msg": "Token 无效"}), 401

    return jsonify({"msg": "鉴权通过", "user": token}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)