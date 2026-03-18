"""
Pytest 配置文件
共享 fixtures 和钩子
"""

import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==================== 通用 Fixtures ====================

@pytest.fixture(scope="session")
def app():
    """
    创建测试应用实例
    作用域: session（整个测试会话共享）
    """
    # from myapp import create_app
    # app = create_app(testing=True)
    # yield app
    pass


@pytest.fixture
def client(app):
    """
    创建测试客户端
    作用域: function（每个测试函数重新创建）
    """
    # return app.test_client()
    pass


@pytest.fixture
def db(app):
    """
    数据库 fixture，带清理
    """
    # from myapp import db as _db
    # _db.create_all()
    # yield _db
    # _db.drop_all()
    pass


@pytest.fixture
def sample_user():
    """
    示例用户数据
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def auth_headers(sample_user):
    """
    认证请求头
    """
    # token = generate_token(sample_user)
    # return {"Authorization": f"Bearer {token}"}
    pass


# ==================== Mock Fixtures ====================

@pytest.fixture
def mock_external_api(mocker):
    """
    Mock 外部 API 调用
    """
    # return mocker.patch('myapp.services.external_api.call')
    pass


@pytest.fixture
def mock_datetime(mocker):
    """
    Mock datetime.now()
    """
    # from datetime import datetime
    # mock = mocker.patch('myapp.utils.datetime')
    # mock.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    # return mock
    pass


# ==================== Pytest Hooks ====================

def pytest_configure(config):
    """
    pytest 配置钩子
    """
    # 注册自定义标记
    config.addinivalue_line("markers", "slow: 标记慢速测试")
    config.addinivalue_line("markers", "integration: 标记集成测试")
    config.addinivalue_line("markers", "e2e: 标记端到端测试")


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集行为
    """
    # 示例：自动给没有标记的测试添加 unit 标记
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# ==================== 辅助函数 ====================

def load_fixture_data(filename: str) -> dict:
    """
    加载测试数据文件
    """
    import json
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(fixture_path) as f:
        return json.load(f)
