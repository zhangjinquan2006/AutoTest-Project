# webdriver 网页内驱动软件
# EdgeChromiumDriverManager Edge驱动管理工具

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def test_web_login_success():
    """测试：在 Edge 网页上真实输入账号密码，点击登录"""

    # 1. 启动 Edge 浏览器（webdriver-manager 会自动帮你下载匹配的驱动）
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)

    try:
        # 2. 打开你的 Flask 登录页面
        driver.get("http://127.0.0.1:5000/")

        # 3. 找到输入框和按钮，并填入数据  element元素
        # （前提：你的 Flask 网页里 input 的 name 必须是 username 和 password）
        driver.find_element(By.NAME, "username").send_keys("auth_user")
        driver.find_element(By.NAME, "password").send_keys("123456")

        # 4. 找到登录按钮并点击
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 5. 等待页面加载
        time.sleep(3)  # 多等一会儿

        # 6. 打印一下当前的源码，看看究竟抓到了什么！
        print("=== 当前网页源码 ===")
        print(driver.page_source)

        # 7. 断言
        assert "注册成功" in driver.page_source
        print("✅ UI 自动化测试通过：注册成功！")

    finally:
        # 7. 关闭浏览器
        driver.quit()