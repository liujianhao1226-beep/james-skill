# {{PROJECT_NAME}}

{{SHORT_DESCRIPTION}}

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
# 使用 pip
pip install {{package_name}}

# 或从源码安装
git clone {{repo_url}}
cd {{project_name}}
pip install -e .
```

## Quick Start

```python
from {{package_name}} import {{MainClass}}

# 基本用法示例
client = {{MainClass}}()
result = client.do_something()
print(result)
```

## Usage

### Basic Usage

```python
# 代码示例
```

### Advanced Usage

```python
# 高级用法示例
```

## Configuration

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `param1` | `str` | `""` | 参数1描述 |
| `param2` | `int` | `10` | 参数2描述 |

## API Reference

详见 [API 文档](docs/api.md)

## Development

### Setup

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

```bash
# 格式化
ruff format .

# 检查
ruff check .
```

## Contributing

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## License

{{LICENSE}} - 详见 [LICENSE](LICENSE) 文件

## Changelog

详见 [CHANGELOG.md](CHANGELOG.md)
