---
name: generate-tests
description: |
  为代码生成单元测试和集成测试。
  触发场景：用户说「帮我写测试」「生成测试用例」「add tests」「write tests」「测试覆盖率」「这个函数怎么测试」「写几个 test」「generate tests」「帮我写单元测试」「加一下测试」。
  会在用户粘贴代码并要求「写测试」或「覆盖」时触发。
---

# Generate Tests Skill

写可维护的测试，不写凑数的测试。

## 第一步：确认测试策略

生成之前快速确认：

1. **测什么？**
   - 单个函数/方法 → 单元测试
   - 多个组件交互 → 集成测试
   - 完整用户流程 → E2E 测试
   - 已有代码补测试 vs 新代码 TDD

2. **用什么框架？**
   - 项目里已有测试框架 → 直接用，不换
   - 没有指定 → 根据语言推断：Python→pytest，JS/TS→Vitest 或 Jest，Go→testing，Rust→built-in

3. **Mock 对象？**
   - 测纯函数（无外部依赖）→ 不需要 mock
   - 有数据库/API/文件系统调用 → 必须 mock 外部依赖

## AAA 结构（每个测试必须遵循）

```python
def test_extracts_username_from_email():
    # Arrange — 准备数据
    email = "john.doe@example.com"

    # Act — 调用被测函数
    result = extract_username(email)

    # Assert — 验证结果
    assert result == "john.doe"
```

**BAD 示例（违反 AAA）：**
```python
def test():  # 连名字都没有
    # 前面一大段 act 和 assert 混在一起
    assert extract_username("a@b.com") == "a"
    assert extract_username("b@c.com") == "b"  # 多个断言，只第一个失败能定位
```

## 好测试命名规范

```
test_<函数名>_<场景>_<预期结果>
```

| 类型 | 示例 |
|---|---|
| 正常路径 | `test_add_numbers_returns_sum` |
| 边界值 | `test_add_numbers_with_zero_returns_sum` |
| 错误输入 | `test_add_numbers_with_none_raises_type_error` |
| 特殊值 | `test_add_numbers_with_empty_string_concatenates` |

## 测试优先级

**先覆盖：**
1. 核心业务逻辑（没有它系统就无法工作）
2. 边界条件（0、-1、空、最大值）
3. 错误处理（抛异常、返回错误码）

**后覆盖或跳过：**
- getter/setter（除非有实际逻辑）
- 简单的赋值语句
- 第三方库的包装函数

## 常用 Mock 模式

**只 mock 副作用，不 mock 逻辑：**

```python
# ✅ 正确：mock 了真正的外部调用
def test_sends_welcome_email(mocker):
    mock_send = mocker.patch('app.email.send')
    register_user("alice@example.com")
    mock_send.assert_called_once_with("alice@example.com", template="welcome")

# ❌ 错误：把被测函数内部逻辑也 mock 了
mock_register = mocker.patch('app.register_user', return_value={"id": 1})
```

## 常见错误

| 错误 | 问题 | 正确做法 |
|---|---|---|
| `time.sleep(1)` | 不稳定，慢 | 用 mocker 模拟时间 |
| 断言过多 | 失败时难定位 | 每个 test 一个主要断言 |
| 测试依赖执行顺序 | 隔离性差 | 加 `setup` 独立初始化 |
| 测试不测行为测实现 | 重构就挂 | 测「输入→输出」，不测「怎么实现的」|

## 输出

- 直接写入选定测试文件（如果路径明确）
- 如果没给路径，在对话中输出完整代码块
- 复杂测试加一行注释说明测了什么
