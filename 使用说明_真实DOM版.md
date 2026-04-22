# 漏斗分析V2 BETA 自动化测试脚本使用说明

这份脚本是基于**真实测试环境**（`https://ll.parllay.cn/apps/reports/report-list/self/funnel-v2/`）的页面结构生成的，可以直接运行。

## 1. 准备工作

确保你已经按照之前的步骤安装了环境：
```bash
pip install pytest pytest-playwright
playwright install chromium
```

## 2. 保存登录状态（必须执行）

为了让脚本能自动登录，你需要先手动登录一次保存状态：

1. 打开命令行（cmd）
2. 运行以下命令：
   ```bash
   python -m playwright codegen --save-storage=auth.json https://ll.parllay.cn/login#/login/email
   ```
3. 会弹出一个浏览器窗口，在里面输入账号 `cuicailu@ifenghuotai.cn` 和密码 `123456Aa` 登录
4. 登录成功进入系统后，**直接关闭浏览器窗口**
5. 此时当前目录下会生成一个 `auth.json` 文件，里面保存了你的登录状态

## 3. 运行测试脚本

把 `test_funnel_v2_real.py` 和 `auth.json` 放在同一个文件夹下，在命令行运行：

```bash
# 运行测试并显示浏览器界面（推荐，能看到执行过程）
python -m pytest test_funnel_v2_real.py -v --headed --browser-context-args="{\"storage_state\": \"auth.json\"}"

# 如果不想看到浏览器界面，在后台静默运行：
python -m pytest test_funnel_v2_real.py -v --browser-context-args="{\"storage_state\": \"auth.json\"}"
```

## 4. 脚本覆盖的测试用例

当前脚本覆盖了以下核心功能点：

1. **TC-VF-001**：创建生命周期漏斗并配置步骤（添加"所有创建的联系人"和"市场线索"）
2. **TC-VF-003**：删除漏斗步骤（验证删除按钮功能）
3. **TC-SR-001**：保存报表弹窗及权限设置（验证弹窗元素和权限选项）
4. **TC-VF-008**：数据筛选功能验证（验证日期和过滤器选项）
5. **TC-VF-009**：图表类型切换（验证垂直/卧式漏斗切换）

## 5. 常见问题

- **报错 `TimeoutError`**：可能是网络慢导致页面没加载出来，可以重新运行一次。
- **报错 `auth.json not found`**：说明第2步没有执行成功，请重新执行第2步保存登录状态。
- **测试失败（Failed）**：如果某个用例失败，说明页面元素可能发生了变化，或者功能存在Bug，可以把报错信息发给我，我来帮你调整脚本。
