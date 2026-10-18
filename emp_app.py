from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)


def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',  # ⚠️ 这里换成你真实的 MySQL 密码
        database='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_user WHERE username=%s AND password=%s",
                   (data.get('username'), data.get('password')))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"token": "emp_token_999"}), 200
    return jsonify({"msg": "登录失败"}), 401


@app.route('/api/add_emp', methods=['POST'])
def add_emp():
    token = request.headers.get('Authorization')
    if token != "Bearer emp_token_999":
        return jsonify({"msg": "没权限"}), 401

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employee (emp_name, department, salary) VALUES (%s, %s, %s)",
                   (data.get('name'), data.get('dept'), data.get('salary')))
    conn.commit()
    conn.close()
    return jsonify({"msg": "添加成功"}), 200


@app.route('/web/employees')
def emp_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee")
    emps = cursor.fetchall()
    conn.close()

    # 这里是绝对规范的缩进
    html = "<h2>员工管理系统</h2><table border='1'><tr><th>ID</th><th>姓名</th><th>部门</th><th>薪资</th></tr>"
    for e in emps:
        html += f"<tr><td>{e['id']}</td><td>{e['emp_name']}</td><td>{e['department']}</td><td>{e['salary']}</td></tr>"
    html += "</table>"
    return html


if __name__ == '__main__':
    app.run(port=5000, debug=True)