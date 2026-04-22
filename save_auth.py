"""
手动生成 auth.json 登录态文件。

使用场景：
  - 首次使用时运行一次
  - auth.json 过期（登录态失效）时重新运行
  - 账号密码变更后重新运行

运行方式：
  python save_auth.py

运行后会打开浏览器窗口，自动完成登录，成功后关闭浏览器并保存 auth.json。
"""

from playwright.sync_api import sync_playwright
import os

LOGIN_URL = "https://ll.parllay.cn/login"
USERNAME = "cuicailu@ifenghuotai.cn"
PASSWORD = "123456Aa"
AUTH_FILE = os.path.join(os.path.dirname(__file__), "auth.json")


def save_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"正在访问登录页：{LOGIN_URL}")
        page.goto(LOGIN_URL)

        # 等待登录表单
        page.wait_for_selector(
            'input[type="text"], input[name="username"], input[placeholder*="邮箱"], input[placeholder*="账号"]',
            state='visible', timeout=15000
        )

        # 填写账号
        username_input = page.locator(
            'input[type="text"], input[name="username"], input[placeholder*="邮箱"], input[placeholder*="账号"]'
        ).first
        username_input.fill(USERNAME)

        # 填写密码
        password_input = page.locator('input[type="password"]').first
        password_input.fill(PASSWORD)

        # 点击登录
        login_btn = page.locator(
            'button[type="submit"], button:has-text("登录"), button:has-text("登 录")'
        ).first
        login_btn.click()

        # 等待登录成功
        print("等待登录成功...")
        page.wait_for_selector(".ant-layout-sider", state='visible', timeout=20000)
        print("✅ 登录成功！")

        # 保存登录态
        context.storage_state(path=AUTH_FILE)
        print(f"✅ 登录态已保存到：{AUTH_FILE}")

        browser.close()
        print("浏览器已关闭，可以运行测试了：")
        print("  python -m pytest test_funnel_v2_real.py -v --headed")


if __name__ == "__main__":
    save_auth()
