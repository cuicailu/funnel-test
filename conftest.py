import pytest
import os
from playwright.sync_api import Page, Browser, BrowserContext

# ============================================================
# 登录配置（账号密码直接写在这里，无需手动维护 auth.json）
# ============================================================
LOGIN_URL = "https://ll.parllay.cn/login"
USERNAME = "cuicailu@ifenghuotai.cn"
PASSWORD = "123456Aa"
# 登录后跳转到漏斗V2页面的标志元素（确认已成功登录）
LOGIN_SUCCESS_SELECTOR = ".ant-layout-sider"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    优先使用 auth.json（如果存在且有效）；
    否则忽略，由 auto_login fixture 在每次 session 开始时自动登录。
    """
    auth_file = os.path.join(os.path.dirname(__file__), "auth.json")
    if os.path.exists(auth_file):
        return {
            **browser_context_args,
            "storage_state": auth_file,
        }
    return browser_context_args


@pytest.fixture(scope="session", autouse=True)
def auto_login(browser: Browser):
    """
    Session 级别自动登录 fixture。
    - 如果 auth.json 存在，跳过登录（直接复用已有登录态）。
    - 如果 auth.json 不存在，自动执行账号密码登录，并将登录态保存到 auth.json，
      供本次 session 内所有测试复用。
    """
    auth_file = os.path.join(os.path.dirname(__file__), "auth.json")

    # auth.json 已存在，跳过登录
    if os.path.exists(auth_file):
        yield
        return

    # 创建一个临时 context 执行登录
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto(LOGIN_URL)
        # 等待登录表单出现
        page.wait_for_selector('input[type="text"], input[name="username"], input[placeholder*="邮箱"], input[placeholder*="账号"]',
                               state='visible', timeout=15000)

        # 填写账号
        username_input = page.locator(
            'input[type="text"], input[name="username"], input[placeholder*="邮箱"], input[placeholder*="账号"]'
        ).first
        username_input.fill(USERNAME)

        # 填写密码
        password_input = page.locator('input[type="password"]').first
        password_input.fill(PASSWORD)

        # 点击登录按钮
        login_btn = page.locator(
            'button[type="submit"], button:has-text("登录"), button:has-text("登 录")'
        ).first
        login_btn.click()

        # 等待登录成功（侧边栏出现）
        page.wait_for_selector(LOGIN_SUCCESS_SELECTOR, state='visible', timeout=20000)

        # 保存登录态到 auth.json
        context.storage_state(path=auth_file)
        print(f"\n✅ 自动登录成功，登录态已保存到 {auth_file}")

    except Exception as e:
        print(f"\n❌ 自动登录失败: {e}")
        print("请手动运行以下命令生成 auth.json：")
        print("  python save_auth.py")
        raise

    finally:
        page.close()
        context.close()

    yield

    # Session 结束后清理 auth.json（可选，注释掉则下次运行复用登录态）
    # if os.path.exists(auth_file):
    #     os.remove(auth_file)
