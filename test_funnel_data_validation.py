import pytest
from playwright.sync_api import Page, expect
import json

class TestFunnelDataValidation:
    """
    漏斗分析V2 - 深度数据验证测试用例
    """

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        # 访问漏斗V2页面
        page.goto('https://ll.parllay.cn/apps/reports/report-list/self/funnel-v2/')
        # 等待页面加载完成
        page.wait_for_selector('.chart-column-barfunnel-filter', state='visible')
        yield

    def test_vf_data_consistency(self, page: Page):
        """
        用例编号：TC-VF-DATA-001
        测试场景：验证接口返回的漏斗数据与页面图表渲染的数据是否一致
        验证深度：业务逻辑层（接口数据 vs 页面UI）
        """
        # 1. 开启网络请求监听，捕获漏斗数据接口的响应
        api_response_data = {}
        
        def handle_response(response):
            # 监听漏斗数据接口
            if '/report/data/funnel-v2' in response.url and response.status == 200:
                try:
                    data = response.json()
                    if data.get('success') and 'data' in data:
                        # 保存接口返回的真实数据，例如：{"所有创建的联系人": 16396, "市场线索": 11}
                        api_response_data.update(data['data'])
                except Exception as e:
                    print(f"解析接口数据失败: {e}")

        page.on("response", handle_response)

        # 2. 在页面上配置漏斗步骤，触发接口请求
        # 点击添加属性
        add_btn = page.locator('button.ant-dropdown-trigger:has-text("添加属性")')
        add_btn.click()
        
        # 选择第一步：所有创建的联系人
        step1 = page.locator('li[role="menuitem"]:has-text("所有创建的联系人")')
        step1.click()
        
        # 再次点击添加属性
        add_btn.click()
        
        # 选择第二步：市场线索
        step2 = page.locator('li[role="menuitem"]:has-text("市场线索")')
        step2.click()

        # 3. 等待图表渲染完成（等待接口请求完成并渲染）
        page.wait_for_selector('.chartGraph canvas', state='visible', timeout=10000)
        # 额外等待1秒确保动画和文字渲染完成
        page.wait_for_timeout(1000)

        # 4. 验证：接口是否成功返回了数据
        assert len(api_response_data) >= 2, "未成功拦截到漏斗数据接口的响应"
        
        # 获取接口中的预期数值
        expected_step1_count = api_response_data.get("所有创建的联系人", 0)
        expected_step2_count = api_response_data.get("市场线索", 0)
        
        # 格式化预期数值（页面上会加千位分隔符，如 16396 -> 16,396）
        expected_step1_text = f"{expected_step1_count:,}"
        expected_step2_text = f"{expected_step2_count:,}"

        # 5. 验证：页面图表上是否正确渲染了这些数值
        # 查找页面上包含这些数字的元素
        # 注意：这里使用精确匹配文本，确保图表上确实显示了这个数字
        step1_element = page.locator(f'text="{expected_step1_text}"').first
        step2_element = page.locator(f'text="{expected_step2_text}"').first

        # 断言页面元素可见
        expect(step1_element).to_be_visible(timeout=5000)
        expect(step2_element).to_be_visible(timeout=5000)
        
        print(f"\n✅ 数据一致性验证通过！")
        print(f"接口返回数据: 所有创建的联系人={expected_step1_count}, 市场线索={expected_step2_count}")
        print(f"页面渲染数据: {expected_step1_text}, {expected_step2_text}")

        # 6. 验证：转化率计算逻辑
        if expected_step1_count > 0:
            # 计算预期转化率 (保留两位小数)
            expected_rate = round((expected_step2_count / expected_step1_count) * 100, 2)
            expected_rate_text = f"{expected_rate}%"
            
            # 验证页面上是否显示了正确的转化率
            rate_element = page.locator(f'text="{expected_rate_text}"').first
            expect(rate_element).to_be_visible(timeout=5000)
            print(f"✅ 转化率计算验证通过！预期: {expected_rate_text}")
