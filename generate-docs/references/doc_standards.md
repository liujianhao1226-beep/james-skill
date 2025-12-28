# 文档规范指南

## 文档类型与用途

| 类型 | 用途 | 受众 |
|------|------|------|
| README | 项目概述和快速入门 | 所有开发者 |
| API 文档 | 接口详细说明 | API 使用者 |
| 代码注释 | 解释复杂逻辑 | 代码维护者 |
| 架构文档 | 系统设计说明 | 架构师/高级开发 |
| 用户指南 | 使用说明 | 最终用户 |

## 文档原则

### 1. 说明 Why，而不只是 What
```python
# ❌ 不好的注释
x = x + 1  # x 加 1

# ✅ 好的注释
x = x + 1  # 补偿数组索引从 0 开始的偏移
```

### 2. 保持同步
- 代码改了文档也要改
- 定期检查文档时效性
- 删除过时的文档

### 3. 简洁明了
- 避免冗长的描述
- 使用列表和表格
- 一图胜千言

### 4. 包含示例
```python
def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串
    
    Example:
        >>> parse_date("2024-01-15")
        datetime(2024, 1, 15, 0, 0, 0)
        
        >>> parse_date("2024/01/15")
        datetime(2024, 1, 15, 0, 0, 0)
    """
```

## 各语言文档格式

### Python (Docstring)

#### Google 风格
```python
def function(arg1: str, arg2: int) -> bool:
    """简短描述。

    更详细的描述，可以
    跨越多行。

    Args:
        arg1: 参数1的描述。
        arg2: 参数2的描述。

    Returns:
        返回值的描述。

    Raises:
        ValueError: 什么情况下抛出。

    Example:
        >>> function("hello", 42)
        True
    """
```

#### NumPy 风格
```python
def function(arg1, arg2):
    """
    简短描述。

    Parameters
    ----------
    arg1 : str
        参数1的描述。
    arg2 : int
        参数2的描述。

    Returns
    -------
    bool
        返回值的描述。
    """
```

### JavaScript/TypeScript (JSDoc)
```javascript
/**
 * 简短描述
 * 
 * @param {string} arg1 - 参数1的描述
 * @param {number} arg2 - 参数2的描述
 * @returns {boolean} 返回值的描述
 * @throws {Error} 什么情况下抛出
 * @example
 * // 使用示例
 * function("hello", 42) // => true
 */
```

### Go (GoDoc)
```go
// FunctionName 简短描述。
//
// 更详细的描述，解释函数的行为、
// 参数含义和返回值。
//
// Example:
//
//	result := FunctionName("input")
//	fmt.Println(result)
func FunctionName(input string) (string, error) {
```

### Rust (RustDoc)
```rust
/// 简短描述。
///
/// 更详细的描述。
///
/// # Arguments
///
/// * `arg1` - 参数1的描述
///
/// # Returns
///
/// 返回值的描述
///
/// # Examples
///
/// ```
/// let result = function("hello");
/// assert_eq!(result, expected);
/// ```
pub fn function(arg1: &str) -> Result<String, Error> {
```

## Markdown 最佳实践

### 标题层级
```markdown
# 一级标题（文档标题，只用一次）
## 二级标题（主要章节）
### 三级标题（子章节）
#### 四级标题（尽量避免超过四级）
```

### 代码块
````markdown
```python
# 指定语言以获得语法高亮
def hello():
    print("Hello, World!")
```
````

### 表格
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 值1 | 值2 | 值3 |
```

### 链接和图片
```markdown
[链接文字](https://example.com)
![图片描述](path/to/image.png)
```
