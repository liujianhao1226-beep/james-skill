# 常见错误类型速查

## Python 错误

### TypeError
```python
# 原因：类型不匹配
"hello" + 5  # TypeError: can only concatenate str (not "int") to str

# 解决：类型转换
"hello" + str(5)
```

### AttributeError
```python
# 原因：对象没有该属性
None.split()  # AttributeError: 'NoneType' object has no attribute 'split'

# 解决：空值检查
if value is not None:
    value.split()
```

### KeyError
```python
# 原因：字典键不存在
data = {"a": 1}
data["b"]  # KeyError: 'b'

# 解决：使用 get 或检查
data.get("b", default_value)
```

### IndexError
```python
# 原因：索引越界
arr = [1, 2, 3]
arr[5]  # IndexError: list index out of range

# 解决：检查长度
if len(arr) > 5:
    arr[5]
```

## JavaScript 错误

### TypeError
```javascript
// 原因：undefined/null 上调用方法
undefined.map()  // TypeError: Cannot read property 'map' of undefined

// 解决：可选链
data?.map(fn)
```

### ReferenceError
```javascript
// 原因：变量未定义
console.log(foo)  // ReferenceError: foo is not defined

// 解决：声明变量或检查
if (typeof foo !== 'undefined') { ... }
```

### SyntaxError
```javascript
// 原因：JSON 解析失败
JSON.parse("invalid")  // SyntaxError: Unexpected token

// 解决：try-catch
try {
    JSON.parse(str)
} catch (e) {
    console.error('Invalid JSON')
}
```

## Go 错误

### nil pointer dereference
```go
// 原因：对 nil 指针解引用
var p *User
p.Name  // panic: runtime error: invalid memory address

// 解决：nil 检查
if p != nil {
    p.Name
}
```

### index out of range
```go
// 原因：切片越界
arr := []int{1, 2, 3}
arr[5]  // panic: runtime error: index out of range

// 解决：检查长度
if len(arr) > 5 {
    arr[5]
}
```

## 数据库错误

### Connection refused
```
# 原因：数据库未启动或端口错误
# 解决：检查数据库服务状态和连接配置
```

### Deadlock
```
# 原因：事务互相等待
# 解决：统一加锁顺序，减小事务范围
```

### Too many connections
```
# 原因：连接池耗尽
# 解决：增加连接池大小，检查连接泄漏
```
