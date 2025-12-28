# 调试工具指南

## 通用调试技巧

### 日志调试
```python
# Python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"变量值: {var}")
```

```javascript
// JavaScript
console.log('变量值:', var);
console.table(arrayData);  // 表格形式显示数组
console.trace();  // 打印调用栈
```

### 断点调试
- 条件断点：仅在条件满足时暂停
- 日志断点：不暂停，仅打印信息
- 异常断点：抛出异常时自动暂停

## Python 调试工具

### pdb (内置调试器)
```python
import pdb; pdb.set_trace()  # 设置断点

# 常用命令
# n (next) - 执行下一行
# s (step) - 进入函数
# c (continue) - 继续执行
# p var - 打印变量
# l (list) - 显示代码
# q (quit) - 退出
```

### ipdb (增强版 pdb)
```bash
pip install ipdb
```
```python
import ipdb; ipdb.set_trace()
```

### pudb (可视化调试器)
```bash
pip install pudb
python -m pudb script.py
```

## JavaScript 调试工具

### Chrome DevTools
- **Elements**: 检查 DOM
- **Console**: 执行 JS，查看日志
- **Sources**: 断点调试
- **Network**: 网络请求
- **Performance**: 性能分析

### Node.js 调试
```bash
# 启动调试模式
node --inspect script.js

# 使用 Chrome DevTools 连接
chrome://inspect
```

### VS Code 调试
```json
// .vscode/launch.json
{
  "type": "node",
  "request": "launch",
  "name": "Debug",
  "program": "${file}"
}
```

## Go 调试工具

### Delve
```bash
# 安装
go install github.com/go-delve/delve/cmd/dlv@latest

# 调试
dlv debug main.go

# 常用命令
# break main.go:10 - 设置断点
# continue - 继续执行
# next - 下一行
# step - 进入函数
# print var - 打印变量
```

## 性能分析工具

### Python
```bash
# cProfile
python -m cProfile -s cumtime script.py

# memory_profiler
pip install memory_profiler
python -m memory_profiler script.py
```

### JavaScript
```javascript
// 时间测量
console.time('label');
// ... code ...
console.timeEnd('label');

// 内存快照
// Chrome DevTools -> Memory -> Take Heap Snapshot
```

### Go
```go
import "runtime/pprof"

// CPU 分析
f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()

// 查看
// go tool pprof cpu.prof
```
