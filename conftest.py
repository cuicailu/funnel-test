import pytest
from playwright.sync_api import Browser, BrowserContext
import os
import json

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    自动读取 auth.json 登录状态
    auth.json 需要和本文件放在同一目录下
    """
    auth_file = os.path.join(os.path.dirname(__file__), "auth.json")
    if os.path.exists(auth_file):
        return {
            **browser_context_args,
            "storage_state": auth_file,
        }
    return browser_context_args
