import pytest
import requests
import pymysql


# 从数据库拿测试数据
def get_test_data():
    conn = pymysql.connect(host='localhost', user='root', password='123456',
                           database='test_db', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("SELECT '张三' as name, '技术部' as dept, 10000 as salary UNION SELECT '李四', '财务部', 8000")
    data = cursor.fetchall()
    conn.close()
    return [(d['name'], d['dept'], d['salary']) for d in data]


@pytest.fixture
def db_connection():
    conn = pymysql.connect(host='localhost', user='root', password='123456',
                           database='test_db', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    # 把前置清理也注释掉，让它不要再杀张三了！
    # cursor.execute("DELETE FROM employee WHERE emp_name IN ('张三', '李四')")
    # conn.commit()

    yield conn

    # 后置也注释了
    cursor.close()
    conn.close()


# 核心测试：数据驱动添加员工并校验落库
@pytest.mark.parametrize("name, dept, salary", get_test_data())
def test_add_employee_and_check_db(db_connection, name, dept, salary):
    # 1. 拿 Token
    login_res = requests.post("http://127.0.0.1:5000/api/login", json={"username": "admin", "password": "123456"})
    token = login_res.json()["token"]

    # 2. 发请求添加员工
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": name, "dept": dept, "salary": salary}
    res = requests.post("http://127.0.0.1:5000/api/add_emp", json=payload, headers=headers)
    assert res.status_code == 200

    # 3. 数据库校验：去查有没有这个人，部门对不对
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM employee WHERE emp_name = %s", (name,))
    db_res = cursor.fetchone()

    assert db_res is not None, f"接口返回成功，但数据库没找到 {name}！"
    assert db_res["department"] == dept, "部门不对！"
    assert db_res["salary"] == salary, "薪资不对！"