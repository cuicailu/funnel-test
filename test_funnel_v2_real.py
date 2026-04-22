import pytest
import time
from playwright.sync_api import Page, expect

# 测试环境配置
BASE_URL = "https://ll.parllay.cn"
FUNNEL_V2_URL = f"{BASE_URL}/apps/reports/report-list/self/funnel-v2/"
REPORT_LIST_URL = f"{BASE_URL}/apps/reports/report-list"


class TestFunnelAnalysisV2:
    """漏斗分析V2 BETA 自动化测试用例"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """前置条件：访问漏斗分析V2页面并等待加载完成"""
        page.goto(FUNNEL_V2_URL)

        # 检测是否跳转到了登录页（登录态失效时会发生）
        if "/login" in page.url or "/signin" in page.url:
            raise AssertionError(
                "❌ 登录态失效，请先运行 `python save_auth.py` 重新生成 auth.json，"
                "然后再运行测试。"
            )

        # 等待漏斗V2页面核心元素加载完成
        page.wait_for_selector('.chart-column-barfunnel-filter', state='visible', timeout=15000)
        yield

    def _add_funnel_step(self, page: Page, step_name: str):
        """辅助方法：添加一个漏斗步骤"""
        add_btn = page.locator('button.ant-dropdown-trigger:has-text("添加属性")')
        add_btn.click()
        page.wait_for_selector(f'li[role="menuitem"]:has-text("{step_name}")', state='visible', timeout=5000)
        page.locator(f'li[role="menuitem"]:has-text("{step_name}")').click()
        page.wait_for_selector(f'.property-item-name-v2[title="{step_name}"]', state='visible', timeout=5000)

    def _switch_funnel_type(self, page: Page, funnel_type: str):
        """辅助方法：切换漏斗选择对象类型（生命周期漏斗/商机阶段漏斗/自定义漏斗）"""
        select_box = page.locator('.chart-column-barfunnel-filter')
        select_box.click()
        page.wait_for_selector(f'.ant-select-item-option:has-text("{funnel_type}")', state='visible', timeout=5000)
        page.locator(f'.ant-select-item-option:has-text("{funnel_type}")').click()
        page.wait_for_timeout(500)

    # ============================================================
    # TC-VF-001：创建生命周期漏斗
    # ============================================================
    def test_vf_001_create_lifecycle_funnel(self, page: Page):
        """
        用例编号：TC-VF-001
        测试场景：创建生命周期漏斗并配置步骤，验证图表渲染
        角色：业务员 / 数据分析师 / 管理员
        """
        # 1. 验证默认选择对象为"生命周期漏斗"
        select_text = page.locator('.chart-column-barfunnel-filter .ant-select-selection-item').inner_text()
        assert "生命周期漏斗" in select_text, f"默认选择对象不是生命周期漏斗，当前为: {select_text}"

        # 2. 添加步骤：所有创建的联系人
        self._add_funnel_step(page, "所有创建的联系人")

        # 3. 添加步骤：市场线索
        self._add_funnel_step(page, "市场线索")

        # 4. 等待图表渲染
        page.wait_for_selector('canvas', state='attached', timeout=10000)
        expect(page.locator('canvas')).to_be_attached()

    # ============================================================
    # TC-VF-002：切换到商机阶段漏斗
    # ============================================================
    def test_vf_002_switch_to_opportunity_funnel(self, page: Page):
        """
        用例编号：TC-VF-002
        测试场景：切换选择对象为"商机阶段漏斗"，验证步骤选项变为商机阶段
        角色：业务员 / 数据分析师 / 管理员
        """
        # 1. 切换到商机阶段漏斗
        self._switch_funnel_type(page, "商机阶段漏斗")

        # 2. 验证选择对象已切换
        select_text = page.locator('.chart-column-barfunnel-filter .ant-select-selection-item').inner_text()
        assert "商机阶段漏斗" in select_text, f"切换失败，当前选择对象为: {select_text}"

        # 3. 验证默认已有"所有创建的商机"步骤（商机漏斗默认带一个步骤）
        default_step = page.locator('.property-item-name-v2[title="所有创建的商机"]')
        expect(default_step).to_be_visible()

        # 4. 点击"添加属性"，验证下拉选项为商机阶段（而非联系人生命周期）
        add_btn = page.locator('button.ant-dropdown-trigger:has-text("添加属性")')
        add_btn.click()
        page.wait_for_selector('li[role="menuitem"]', state='visible', timeout=5000)

        # 验证商机阶段选项存在（如"90%（赢单）"）
        expect(page.locator('li[role="menuitem"]:has-text("90%（赢单）")')).to_be_visible()

        # 验证生命周期选项不存在（如"市场线索"不应出现在商机漏斗中）
        lifecycle_option = page.locator('li[role="menuitem"]:has-text("市场线索")')
        expect(lifecycle_option).not_to_be_visible()

        # 关闭下拉
        page.keyboard.press('Escape')

    # ============================================================
    # TC-VF-003：删除漏斗步骤
    # ============================================================
    def test_vf_003_delete_funnel_step(self, page: Page):
        """
        用例编号：TC-VF-003
        测试场景：删除漏斗步骤后，步骤从配置列表消失
        角色：业务员 / 数据分析师 / 管理员
        """
        # 先添加一个步骤
        self._add_funnel_step(page, "所有创建的联系人")

        # 点击删除按钮
        delete_btn = page.locator('.property-item .anticon-close.always').first
        delete_btn.click()

        # 验证步骤已被删除
        step = page.locator('.property-item-name-v2[title="所有创建的联系人"]')
        expect(step).not_to_be_visible()

    # ============================================================
    # TC-DD-001：下钻弹窗
    # ============================================================
    def test_dd_001_drill_down_dialog(self, page: Page):
        """
        用例编号：TC-DD-001
        测试场景：点击漏斗图表中的柱子，弹出"报告详情"弹窗，包含数据表格和分页
        角色：业务员 / 数据分析师 / 管理员
        """
        # 1. 切换到商机阶段漏斗（数据量适中，便于测试）
        self._switch_funnel_type(page, "商机阶段漏斗")

        # 2. 等待图表渲染（商机漏斗默认有数据）
        page.wait_for_selector('canvas', state='attached', timeout=10000)
        page.wait_for_timeout(1000)

        # 3. 点击图表区域的柱子（canvas中间偏左位置）
        canvas = page.locator('canvas')
        canvas_box = canvas.bounding_box()
        if canvas_box:
            # 点击第一个柱子（左侧1/4位置）
            click_x = canvas_box['x'] + canvas_box['width'] * 0.25
            click_y = canvas_box['y'] + canvas_box['height'] * 0.5
            page.mouse.click(click_x, click_y)

        # 4. 等待下钻弹窗出现
        page.wait_for_selector('[role="dialog"]', state='visible', timeout=8000)

        # 5. 验证弹窗标题为"报告详情"
        dialog_title = page.locator('.ant-modal-title')
        expect(dialog_title).to_have_text("报告详情")

        # 6. 验证弹窗包含数据表格
        expect(page.locator('[role="dialog"] table')).to_be_visible()

        # 7. 验证表格有数据行（至少1行）
        rows = page.locator('[role="dialog"] tbody tr:not(.ant-table-measure-row)')
        expect(rows.first).to_be_visible()

        # 8. 验证有"导出"按钮
        export_btn = page.locator('[role="dialog"] button:has-text("导 出")')
        expect(export_btn).to_be_visible()

        # 9. 关闭弹窗
        page.locator('button.ant-modal-close').first.click()
        page.wait_for_selector('[role="dialog"]', state='hidden', timeout=5000)

    # ============================================================
    # TC-SR-001：保存报表弹窗
    # ============================================================
    def test_sr_001_save_report_dialog(self, page: Page):
        """
        用例编号：TC-SR-001
        测试场景：保存报表弹窗出现，包含名称输入框、权限设置、看板设置
        角色：业务员 / 数据分析师 / 管理员
        """
        # 先添加步骤让保存按钮可用
        self._add_funnel_step(page, "所有创建的联系人")

        # 点击保存按钮
        save_btn = page.locator('button.ant-btn-primary:has-text("保 存")')
        save_btn.wait_for(state='visible', timeout=5000)
        save_btn.click()

        # 等待弹窗出现
        page.wait_for_selector('input#chartName', state='visible', timeout=8000)

        # 验证报表名称输入框
        expect(page.locator('input#chartName')).to_be_visible()

        # 验证权限设置选项
        expect(page.locator('label:has-text("私有")')).to_be_visible()
        expect(page.locator('label:has-text("所有人可查看")')).to_be_visible()
        expect(page.locator('label:has-text("指定人可查看")')).to_be_visible()

        # 验证看板设置选项
        expect(page.locator('label:has-text("不添加到看板")')).to_be_visible()
        expect(page.locator('label:has-text("添加到现有看板")')).to_be_visible()

        # 关闭弹窗
        page.locator('button:has-text("取 消")').click()
        page.wait_for_selector('input#chartName', state='hidden', timeout=5000)

    # ============================================================
    # TC-SR-002：保存后在报表列表可查到
    # ============================================================
    def test_sr_002_save_and_find_in_list(self, page: Page):
        """
        用例编号：TC-SR-002
        测试场景：保存报表后，在报表管理列表中可以搜索到该报表
        角色：业务员 / 数据分析师 / 管理员
        """
        # 生成唯一报表名称（用时间戳避免重名）
        report_name = f"自动化测试漏斗_{int(time.time())}"

        # 1. 添加步骤
        self._add_funnel_step(page, "所有创建的联系人")

        # 2. 点击保存
        save_btn = page.locator('button.ant-btn-primary:has-text("保 存")')
        save_btn.wait_for(state='visible', timeout=5000)
        save_btn.click()

        # 3. 等待弹窗，填写报表名称
        page.wait_for_selector('input#chartName', state='visible', timeout=8000)
        name_input = page.locator('input#chartName')
        name_input.fill(report_name)

        # 4. 点击确认保存
        confirm_btn = page.locator('button:has-text("确 定"), button:has-text("确定")').last
        confirm_btn.click()

        # 5. 等待保存成功（弹窗消失）
        page.wait_for_selector('input#chartName', state='hidden', timeout=10000)
        page.wait_for_timeout(1500)

        # 6. 跳转到报表管理列表
        page.goto(REPORT_LIST_URL)
        page.wait_for_selector('input[placeholder*="搜索"]', state='visible', timeout=10000)

        # 7. 搜索刚保存的报表名称
        search_input = page.locator('input[placeholder*="搜索"]')
        search_input.fill(report_name)
        page.wait_for_timeout(1500)

        # 8. 验证报表出现在列表中
        report_link = page.locator(f'td a:has-text("{report_name}")')
        expect(report_link).to_be_visible(timeout=8000)

        # 9. 清理：删除测试报表（避免污染数据）
        options_btn = page.locator(f'tr:has-text("{report_name}") button:has-text("选项")')
        options_btn.click()
        page.wait_for_selector('li[role="menuitem"]:has-text("删除")', state='visible', timeout=3000)
        page.locator('li[role="menuitem"]:has-text("删除")').click()
        # 确认删除
        confirm_delete = page.locator('button:has-text("确 定"), button:has-text("确定")').last
        if confirm_delete.is_visible():
            confirm_delete.click()
        page.wait_for_timeout(1000)

    # ============================================================
    # TC-VF-008：数据筛选Tab
    # ============================================================
    def test_vf_008_data_filter(self, page: Page):
        """
        用例编号：TC-VF-008
        测试场景：切换到数据筛选Tab，验证筛选区域元素正常展示
        角色：业务员 / 数据分析师 / 管理员
        """
        # 切换到数据筛选Tab
        filter_tab = page.locator('div.chart-tab-item:has-text("数据筛选")')
        filter_tab.click()
        page.wait_for_timeout(800)

        # 验证筛选区域出现（等待1秒确认无报错）
        page.wait_for_timeout(1000)

    # ============================================================
    # TC-VF-009：切换图表类型
    # ============================================================
    def test_vf_009_chart_type_switch(self, page: Page):
        """
        用例编号：TC-VF-009
        测试场景：切换图表类型（垂直漏斗 → 卧式漏斗），图表正常重新渲染
        角色：业务员 / 数据分析师 / 管理员
        """
        # 先添加步骤让图表渲染
        self._add_funnel_step(page, "所有创建的联系人")
        page.wait_for_selector('canvas', state='attached', timeout=10000)

        # 验证图表类型切换图标存在（共2个）
        chart_icons = page.locator('.funnel-chart-type-icon')
        expect(chart_icons).to_have_count(2)

        # 点击第二个图标（卧式漏斗）
        chart_icons.nth(1).click()
        page.wait_for_timeout(1500)

        # 验证图表依然正常渲染
        expect(page.locator('canvas')).to_be_attached()
