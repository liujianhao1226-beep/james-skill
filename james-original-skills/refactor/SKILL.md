---
name: refactor
description: |
  重构代码以提高可读性、可维护性和性能。
  触发场景：用户说「重构」「优化这段代码」「refactor」「简化一下」「太复杂了」「看起来很乱」「消一下重复」「这个函数太长了」「帮我重构」。
  会在用户粘贴代码并要求「改写」「优化」「简化」时触发。
---

# Refactor Skill

改结构，不改行为。小步前进，每步验证。

## 重构第一原则

**行为不变是底线。** 重构前必须已有测试（或手动验证路径），重构后立刻运行验证。没有测试就不重构——除非是临时实验代码。

## 代码味道检查清单

扫一眼代码，按顺序检查：

| 味道 | 表现 | 优先级 |
|---|---|---|
| 函数过长 | >50 行或嵌套 >3 层 | 高 |
| 重复代码 | copy-paste 超过 2 处 | 高 |
| 变量命名差 | `d`、`tmp`、`data1` | 高 |
| 魔法数字 | 硬编码的数字/字符串无解释 | 中 |
| 过早优化 | 复杂度高但未必需要的抽象 | 中 |
| 神对象/上帝类 | 一个类做所有事情 | 中 |
| 注释解释不了的代码 | 需要注释才能理解逻辑 | 高 |
| 嵌套 if 而非提前 return | `if { if { if {...}}}}` | 中 |

## 重构流程

### Step 1：识别味道，列出改动点

不动手，只观察。列出：
- 要改什么（函数/变量/结构）
- 改成什么（更清晰的命名、提取的函数名）
- 预期收益（更短、更清晰、可测试）

### Step 2：分离改动

每次重构只做**一件事**：
- ❌ 同时改名、提取函数、改逻辑 → 太危险
- ✅ 一次只做：提取函数 / 重命名 / 简化条件 → 每次一步

### Step 3：每步验证

每完成一步：
1. 运行测试（或手动验证核心功能）
2. 正常 → 继续下一步
3. 失败 → 立刻回退，不要继续

### Step 4：输出改动说明

告诉用户做了什么、为什么、以及行为是否保持不变。

## 常用重构操作示例

### 提取函数
```python
# 前
total = sum(item['price'] * item['qty'] for item in cart) + shipping
if total > 100: total *= 0.9

# 后
def calc_subtotal(cart):
    return sum(item['price'] * item['qty'] for item in cart)

def apply_discount(total):
    return total * 0.9 if total > 100 else total

total = apply_discount(calc_subtotal(cart))
```

### 消除魔法数字
```python
# 前
time.sleep(86400)  # wait one day

# 后
SECONDS_PER_DAY = 86400
time.sleep(SECONDS_PER_DAY)
```

### 简化条件（提前 return）
```python
# 前
def validate(user):
    if user is not None:
        if user.is_active:
            if user.has_permission:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

# 后
def validate(user):
    if not user:
        return False
    if not user.is_active:
        return False
    if not user.has_permission:
        return False
    return True
```

## 不重构的情况

以下情况**不动**代码：
- 代码即将废弃（1个月内不再改动）
- 风险太高（复杂金融/医疗/安全关键逻辑）
- 临时脚本（用完即扔）
- 重写比重构代价更低（超过 50% 逻辑需要改写）

## 语气

- 重构前问：「这段代码有测试吗？」——没有测试的高风险重构要先说明风险
- 重构后说：「行为没变，只改了结构」——让用户放心
- 遇到不必要重构的代码，直接说：「这段代码不需要重构，原因如下」
