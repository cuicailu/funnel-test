# 漏斗分析V2 自动化测试脚本

基于 Playwright + pytest 的漏斗分析V2 BETA 功能自动化测试脚本。

## 环境要求

- Python 3.8+
- Windows / Mac

## 安装依赖

```bash
pip install playwright pytest pytest-playwright
python -m playwright install chromium
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `conftest.py` | 登录状态配置，自动加载 auth.json |
| `test_funnel_v2_real.py` | 5条交互流程验证用例 |
| `test_funnel_data_validation.py` | 接口数据与页面数据一致性验证 |

## 使用方法

### 第一步：保存登录状态（只需做一次）

```bash
python -m playwright codegen --save-storage=auth.json https://ll.parllay.cn/login#/login/email
```

在弹出的浏览器中登录系统，登录成功后关闭浏览器，`auth.json` 自动保存。

### 第二步：运行全部测试

```bash
python -m pytest test_funnel_v2_real.py test_funnel_data_validation.py -v --headed -s
```

### 第三步：更新脚本（每次我更新后执行）

```bash
git pull
```

## 当前用例清单

| 编号 | 场景 | 文件 | 状态 |
|---|---|---|---|
| TC-VF-001 | 生命周期漏斗步骤配置+图表渲染 | test_funnel_v2_real.py | ✅ |
| TC-VF-003 | 删除漏斗步骤 | test_funnel_v2_real.py | ✅ |
| TC-VF-008 | 数据筛选Tab切换 | test_funnel_v2_real.py | ✅ |
| TC-VF-009 | 图表类型切换 | test_funnel_v2_real.py | ✅ |
| TC-SR-001 | 保存报表弹窗验证 | test_funnel_v2_real.py | ✅ |
| TC-VF-DATA-001 | 接口数据与页面数据一致性 | test_funnel_data_validation.py | ✅ |
| TC-VF-002 | 商机阶段漏斗 | - | ❌ 待补充 |
| TC-DD-001 | 下钻弹窗数据验证 | - | ❌ 待补充 |
| TC-SR-002 | 保存后报表列表可查到 | - | ❌ 待补充 |
