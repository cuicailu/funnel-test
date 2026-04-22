import pytest
from playwright.sync_api import Page, expect

# 测试环境配置
BASE_URL = "https://ll.parllay.cn"
FUNNEL_V2_URL = f"{BASE_URL}/apps/reports/report-list/self/funnel-v2/"


class TestFunnelAnalysisV2:
    """漏斗分析V2 BETA 自动化测试用例"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """前置条件：访问漏斗分析V2页面并等待加载完成"""
        page.goto(FUNNEL_V2_URL)
        page.wait_for_selector('.chart-column-barfunnel-filter', state='visible', timeout=15000)
        yield

    def _add_funnel_step(self, page: Page, step_name: str):
        """辅助方法：添加一个漏斗步骤"""
        add_btn = page.locator('button.ant-dropdown-trigger:has-text("添加属性")')
        add_btn.click()
        page.wait_for_selector(f'li[role="menuitem"]:has-text("{step_name}")', state='visible', timeout=5000)
        page.locator(f'li[role="menuitem"]:has-text("{step_name}")').click()
        page.wait_for_selector(f'.property-item-name-v2[title="{step_name}"]', state='visible', timeout=5000)

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
        page.wait_for_selector('.chartGraph canvas', state='visible', timeout=10000)
        expect(page.locator('.chartGraph canvas')).to_be_visible()

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

    def test_vf_008_data_filter(self, page: Page):
        """
        用例编号：TC-VF-008
        测试场景：切换到数据筛选Tab，验证筛选区域元素正常展示
        角色：业务员 / 数据分析师 / 管理员
        """
        # 切换到数据筛选Tab
        # 尝试多种选择器，兼容不同版本的页面结构
        filter_tab = page.locator('.chart-tab-item').filter(has_text="数据筛选").last
        filter_tab.click()
        page.wait_for_timeout(800)

        # 验证筛选区域出现
        expect(page.locator('.chart-filter-title:has-text("日期属性")')).to_be_visible(timeout=5000)
        expect(page.locator('.chart-filter-title:has-text("日期范围")')).to_be_visible(timeout=5000)
        expect(page.locator('.chart-filter-title:has-text("其他过滤器")')).to_be_visible(timeout=5000)

    def test_vf_009_chart_type_switch(self, page: Page):
        """
        用例编号：TC-VF-009
        测试场景：切换图表类型（垂直漏斗 → 卧式漏斗），图表正常重新渲染
        角色：业务员 / 数据分析师 / 管理员
        """
        # 先添加步骤让图表渲染
        self._add_funnel_step(page, "所有创建的联系人")
        page.wait_for_selector('.chartGraph canvas', state='visible', timeout=10000)

        # 验证图表类型切换图标存在（共2个）
        chart_icons = page.locator('.funnel-chart-type-icon')
        expect(chart_icons).to_have_count(2)

        # 点击第二个图标（卧式漏斗）
        chart_icons.nth(1).click()
        page.wait_for_timeout(1500)

        # 验证图表依然正常渲染
        expect(page.locator('.chartGraph canvas')).to_be_visible()
