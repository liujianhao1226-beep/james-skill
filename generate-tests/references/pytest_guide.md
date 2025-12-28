# Pytest 使用指南

## 基础用法

### 测试文件命名
```
test_*.py      # 以 test_ 开头
*_test.py      # 以 _test 结尾
```

### 测试函数命名
```python
def test_功能_场景_预期结果():
    pass

# 示例
def test_login_with_valid_credentials_returns_token():
    pass

def test_login_with_invalid_password_raises_error():
    pass
```

### 基本断言
```python
def test_example():
    assert value == expected
    assert value != unexpected
    assert value is None
    assert value is not None
    assert value in collection
    assert isinstance(value, Type)
```

## Fixtures

### 基本 fixture
```python
import pytest

@pytest.fixture
def user():
    return User(name="test", email="test@example.com")

def test_user_name(user):
    assert user.name == "test"
```

### Fixture 作用域
```python
@pytest.fixture(scope="function")  # 每个测试函数（默认）
@pytest.fixture(scope="class")     # 每个测试类
@pytest.fixture(scope="module")    # 每个模块
@pytest.fixture(scope="session")   # 整个测试会话
def my_fixture():
    pass
```

### 带清理的 fixture
```python
@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn  # 测试使用这个值
    conn.close()  # 清理
```

## 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

## 异常测试

```python
def test_raises_exception():
    with pytest.raises(ValueError) as excinfo:
        raise ValueError("invalid value")
    assert "invalid" in str(excinfo.value)
```

## 标记 (Markers)

```python
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.skip(reason="暂时跳过")
def test_skipped():
    pass

@pytest.mark.skipif(condition, reason="条件跳过")
def test_conditional_skip():
    pass

@pytest.mark.xfail(reason="预期失败")
def test_expected_failure():
    pass
```

## 常用命令

```bash
# 运行所有测试
pytest

# 运行指定文件
pytest test_file.py

# 运行指定测试
pytest test_file.py::test_function

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 运行指定标记的测试
pytest -m slow

# 失败时停止
pytest -x

# 并行运行
pytest -n auto

# 覆盖率报告
pytest --cov=src --cov-report=html
```

## conftest.py

```python
# conftest.py - 共享 fixtures 和配置

import pytest

@pytest.fixture(scope="session")
def app():
    """创建测试应用"""
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()
```
