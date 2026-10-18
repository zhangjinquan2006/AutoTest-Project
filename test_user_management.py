# 环境准备：确保你本地 Flask 网站（app.py）正在运行，MySQL 数据库连接正常。数据库里必须有一条 admin / 123456 的用户数据。
# 测试用例 1：调用登录接口，断言返回 200，并从返回的 JSON 中提取 token。
# 测试用例 2：使用上一步拿到的 token，调用注册接口，发送 new_user / password123，断言返回 200。
# 数据库校验：去数据库里查 users 表，断言 new_user 真的存在，且密码正确。
# 清理：测试结束后，删除测试数据 new_user。

import pytest
import requests
import pymysql


@pytest.fixture
def db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    yield conn
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s", ("new_user",))
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 测试数据已清理")


auth_token = None

# 拿取真正的token
def test_take_real_token(db_connection):
    url = "http://127.0.0.1:5000/api/login"
    payload = {"username": "admin", "password": "123456"}
    response = requests.post(url, json=payload)

    assert response.status_code == 200

    real_token = response.json()["token"]

    global auth_token
    auth_token = real_token

# 带着真正的token去注册调用接口
def test_sign_up_token(db_connection):
    cursor = db_connection.cursor()

# 重新登录一次
    sign_url = "http://127.0.0.1:5000/api/login"
    sign_payload = {"username": "admin", "password": "123456"}
    sign_response = requests.post(sign_url, json=sign_payload)

    assert sign_response.status_code == 200

    sign_token = sign_response.json()["token"]

    url = "http://127.0.0.1:5000/register"
    headers = {"Authorization": f"Bearer {sign_token}"}
    payload = {"username": "new_user", "password": "password123"}

    response = requests.post(url, data=payload, headers=headers)
    assert response.status_code == 200

    print(f"接口返回状态码：{response.status_code}")

    # 2. 数据库校验：确认 new_user 真的落库
    cursor.execute("SELECT * FROM users WHERE username = %s", ("new_user",))
    db_result = cursor.fetchone()

    assert db_result is not None, "❌ 注册接口返回成功，但数据库里没数据！"
    assert db_result["username"] == "new_user"
    assert db_result["password"] == "password123"
    print(f"✅ 数据库校验通过：{db_result}")