import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def test_ui_show_employee():
    """测试：UI页面能否正确显示数据库中的员工"""
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)

    try:
        # 1. 打开员工列表网页
        driver.get("http://127.0.0.1:5000/web/employees")
        time.sleep(2)  # 等页面加载

        # 2. 获取网页源码
        page_text = driver.page_source

        # 3. 断言：网页上必须显示“张三”和“技术部”
        assert "张三" in page_text, "UI上没看到张三！"
        assert "技术部" in page_text, "UI上没看到技术部！"
        print("✅ UI自动化测试通过：页面正确渲染了员工数据！")

    finally:
        driver.quit()