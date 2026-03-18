# 代码规范指南

## 通用规范

### 命名规范
| 类型 | 风格 | 示例 |
|------|------|------|
| 类名 | PascalCase | `UserService` |
| 函数/方法 | camelCase / snake_case | `getUserById` / `get_user_by_id` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 变量 | camelCase / snake_case | `userName` / `user_name` |

### 函数规范
- 单一职责：每个函数只做一件事
- 长度限制：建议不超过 50 行
- 参数数量：建议不超过 4 个
- 圈复杂度：建议不超过 10

### 注释规范
- 解释 Why，而不是 What
- 保持注释与代码同步
- 删除注释掉的代码

## 语言特定规范

### Python (PEP 8)
```python
# 正确
def calculate_total(items: list[Item]) -> Decimal:
    """计算订单总金额"""
    return sum(item.price for item in items)

# 错误
def calc(i):  # 命名不清晰
    s = 0
    for x in i: s += x.price
    return s
```

### JavaScript/TypeScript
```typescript
// 正确
async function fetchUser(userId: string): Promise<User> {
  const response = await api.get(`/users/${userId}`);
  return response.data;
}

// 错误
async function getU(id) {  // 无类型，命名不清晰
  return (await api.get('/users/' + id)).data;
}
```

### Go
```go
// 正确
func (s *UserService) GetUserByID(ctx context.Context, id string) (*User, error) {
    if id == "" {
        return nil, ErrInvalidID
    }
    return s.repo.FindByID(ctx, id)
}

// 错误
func getUser(id string) *User {  // 未导出，无 context，忽略错误
    u, _ := repo.Find(id)
    return u
}
```

## 代码异味识别

| 异味 | 描述 | 解决方案 |
|------|------|----------|
| 重复代码 | 相似逻辑出现多处 | 提取公共函数 |
| 过长函数 | 函数超过 50 行 | 拆分子函数 |
| 过大类 | 类职责过多 | 拆分类 |
| 长参数列表 | 参数超过 4 个 | 使用对象封装 |
| 魔法数字 | 硬编码数值 | 提取常量 |
