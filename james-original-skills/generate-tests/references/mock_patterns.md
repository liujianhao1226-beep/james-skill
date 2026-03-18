# Mock 模式指南

## Python unittest.mock

### 基本 Mock
```python
from unittest.mock import Mock, MagicMock, patch

# 创建 mock 对象
mock = Mock()
mock.method.return_value = "mocked"
assert mock.method() == "mocked"

# 检查调用
mock.method.assert_called_once()
mock.method.assert_called_with(arg1, arg2)
```

### patch 装饰器
```python
# 替换模块中的对象
@patch('module.ClassName')
def test_with_mock(MockClass):
    instance = MockClass.return_value
    instance.method.return_value = "mocked"
    
    result = function_under_test()
    
    MockClass.assert_called_once()

# 作为上下文管理器
def test_with_context():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = function_under_test()
```

### patch.object
```python
# 替换对象的属性
@patch.object(ClassName, 'method_name')
def test_method(mock_method):
    mock_method.return_value = "mocked"
```

### MagicMock
```python
# 支持魔术方法
mock = MagicMock()
mock.__str__.return_value = "mocked string"
mock.__len__.return_value = 5

assert str(mock) == "mocked string"
assert len(mock) == 5
```

### side_effect
```python
# 抛出异常
mock.method.side_effect = ValueError("error")

# 返回不同值
mock.method.side_effect = [1, 2, 3]

# 自定义函数
mock.method.side_effect = lambda x: x * 2
```

## pytest-mock

```python
def test_with_mocker(mocker):
    # mocker 是 pytest-mock 提供的 fixture
    mock_func = mocker.patch('module.function')
    mock_func.return_value = "mocked"
    
    result = function_under_test()
    
    mock_func.assert_called_once()
```

## JavaScript Jest Mock

### 基本 Mock
```javascript
// Mock 函数
const mockFn = jest.fn();
mockFn.mockReturnValue('mocked');

expect(mockFn()).toBe('mocked');
expect(mockFn).toHaveBeenCalled();
```

### Mock 模块
```javascript
// 自动 mock
jest.mock('./module');

// 手动实现
jest.mock('./module', () => ({
  function: jest.fn().mockReturnValue('mocked')
}));
```

### Mock 实现
```javascript
const mockFn = jest.fn()
  .mockReturnValueOnce('first')
  .mockReturnValueOnce('second')
  .mockReturnValue('default');

// 异步 mock
mockFn.mockResolvedValue('async result');
mockFn.mockRejectedValue(new Error('async error'));
```

## Go Mock (gomock)

```go
// 生成 mock
//go:generate mockgen -source=interface.go -destination=mock_interface.go

func TestWithMock(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockService := NewMockService(ctrl)
    mockService.EXPECT().
        Method(gomock.Any()).
        Return("mocked", nil)

    result, err := functionUnderTest(mockService)
    assert.NoError(t, err)
    assert.Equal(t, "mocked", result)
}
```

## Mock 最佳实践

1. **只 Mock 外部依赖** - 数据库、API、文件系统
2. **不要 Mock 被测代码** - 测试真实逻辑
3. **验证交互** - 确保 mock 被正确调用
4. **保持简单** - 避免过度复杂的 mock 设置
5. **使用 Fake 对象** - 某些场景比 Mock 更好
