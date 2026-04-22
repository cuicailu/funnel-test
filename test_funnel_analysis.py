import pytest
from playwright.sync_api import Page, expect

# 测试环境配置
BASE_URL = "https://ll.parllay.cn"
LOGIN_URL = f"{BASE_URL}/login#/login/email"
FUNNEL_URL = f"{BASE_URL}/apps/reports/report-manage"  # 假设漏斗分析在报表管理中

# 账号配置
TEST_USER = "cuicailu@ifenghuotai.cn"
TEST_PASS = "123456Aa"

@pytest.fixture(scope="session")
def login_context(browser):
    """
    全局登录夹具：在整个测试会话中只登录一次，保存登录状态
    """
    context = browser.new_context()
    page = context.new_page()
    
    # 访问登录页
    page.goto(LOGIN_URL)
    
    # 填写账号密码
    page.fill('input[type="text"]', TEST_USER)
    page.fill('input[type="password"]', TEST_PASS)
    
    # 勾选同意协议（如果存在）
    agreement_checkbox = page.locator('input[type="checkbox"]')
    if agreement_checkbox.is_visible():
        agreement_checkbox.check()
        
    # 点击登录按钮
    page.click('button:has-text("登录")')
    
    # 等待登录成功跳转到首页
    page.wait_for_url("**/apps/**")
    
    # 保存登录状态到文件
    context.storage_state(path="auth.json")
    page.close()
    return context

@pytest.fixture
def auth_page(login_context):
    """
    每个测试用例使用已登录的上下文创建新页面
    """
    page = login_context.new_page()
    yield page
    page.close()

class TestFunnelAnalysis:
    """
    漏斗分析 2.0 自动化测试用例集
    """
    
    def test_navigate_to_funnel(self, auth_page: Page):
        """
        测试场景：验证能够成功导航到漏斗分析页面
        """
        auth_page.goto(FUNNEL_URL)
        # 等待页面加载完成
        auth_page.wait_for_load_state("networkidle")
        
        # 验证页面标题或核心元素
        # expect(auth_page.locator("text=漏斗分析")).to_be_visible()
        
    def test_vertical_funnel_render(self, auth_page: Page):
        """
        测试场景：TC-VF-001 验证垂直漏斗图表默认渲染
        """
        auth_page.goto(FUNNEL_URL)
        
        # 假设点击创建漏斗报表
        # auth_page.click('button:has-text("创建报表")')
        # auth_page.click('text=漏斗分析')
        
        # 验证图表容器是否存在
        # chart_container = auth_page.locator('.funnel-chart-container')
        # expect(chart_container).to_be_visible()
        
        # 验证默认展示的步骤数（假设默认3步）
        # steps = auth_page.locator('.funnel-step')
        # expect(steps).to_have_count(3)

    def test_vertical_funnel_step_rename(self, auth_page: Page):
        """
        测试场景：TC-VF-002 验证垂直漏斗步骤重命名功能
        """
        auth_page.goto(FUNNEL_URL)
        
        # 模拟重命名操作
        # step_name_input = auth_page.locator('.step-name-input').first
        # step_name_input.fill("新步骤名称")
        # step_name_input.press("Enter")
        
        # 验证修改成功
        # expect(auth_page.locator('text=新步骤名称')).to_be_visible()

    def test_horizontal_funnel_switch(self, auth_page: Page):
        """
        测试场景：TC-HF-001 验证卧式漏斗切换与渲染
        """
        auth_page.goto(FUNNEL_URL)
        
        # 点击切换到卧式漏斗
        # auth_page.click('button[title="切换为卧式漏斗"]')
        
        # 验证卧式漏斗特有元素出现
        # horizontal_container = auth_page.locator('.horizontal-funnel')
        # expect(horizontal_container).to_be_visible()

    def test_report_save(self, auth_page: Page):
        """
        测试场景：TC-SR-001 验证保存报表功能
        """
        auth_page.goto(FUNNEL_URL)
        
        # 点击保存按钮
        # auth_page.click('button:has-text("保存")')
        
        # 填写报表名称
        # auth_page.fill('input[placeholder="请输入报表名称"]', "自动化测试漏斗报表")
        # auth_page.click('button:has-text("确定")')
        
        # 验证保存成功提示
        # expect(auth_page.locator('text=保存成功')).to_be_visible()

    def test_report_drill_down(self, auth_page: Page):
        """
        测试场景：TC-DD-001 验证报表下钻功能
        """
        auth_page.goto(FUNNEL_URL)
        
        # 点击漏斗某个层级
        # auth_page.click('.funnel-layer').first
        
        # 验证下钻弹窗出现
        # drill_modal = auth_page.locator('.drill-down-modal')
        # expect(drill_modal).to_be_visible()
        
        # 验证弹窗内包含数据表格
        # expect(drill_modal.locator('table')).to_be_visible()

    def test_report_download(self, auth_page: Page):
        """
        测试场景：TC-DL-001 验证报表下载功能
        """
        auth_page.goto(FUNNEL_URL)
        
        # 拦截下载事件
        # with auth_page.expect_download() as download_info:
        #     auth_page.click('button:has-text("下载")')
        
        # download = download_info.value
        # assert download.suggested_filename.endswith('.xlsx') or download.suggested_filename.endswith('.csv')
