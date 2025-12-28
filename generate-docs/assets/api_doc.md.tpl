# {{API_NAME}} API 文档

## 概述

{{API_DESCRIPTION}}

**Base URL**: `{{BASE_URL}}`

**版本**: `{{VERSION}}`

## 认证

{{AUTH_DESCRIPTION}}

```bash
# 请求头示例
Authorization: Bearer <token>
```

## 通用响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误响应
```json
{
  "code": 40001,
  "message": "错误描述",
  "details": { ... }
}
```

## 错误码

| 错误码 | 描述 |
|--------|------|
| 40001 | 参数错误 |
| 40101 | 未授权 |
| 40301 | 禁止访问 |
| 40401 | 资源不存在 |
| 50001 | 服务器内部错误 |

---

## Endpoints

### {{RESOURCE_NAME}}

#### 获取列表

```
GET /api/v1/{{resource}}
```

**请求参数**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `page` | int | 否 | 页码，默认 1 |
| `page_size` | int | 否 | 每页数量，默认 20 |
| `keyword` | string | 否 | 搜索关键词 |

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "xxx",
        "name": "xxx",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

#### 获取详情

```
GET /api/v1/{{resource}}/{id}
```

**路径参数**

| 参数 | 类型 | 描述 |
|------|------|------|
| `id` | string | 资源 ID |

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "xxx",
    "name": "xxx",
    "description": "xxx",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

#### 创建

```
POST /api/v1/{{resource}}
```

**请求体**

```json
{
  "name": "xxx",
  "description": "xxx"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 名称 |
| `description` | string | 否 | 描述 |

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "newly_created_id"
  }
}
```

---

#### 更新

```
PUT /api/v1/{{resource}}/{id}
```

**请求体**

```json
{
  "name": "new_name",
  "description": "new_description"
}
```

---

#### 删除

```
DELETE /api/v1/{{resource}}/{id}
```

**响应示例**

```json
{
  "code": 0,
  "message": "success"
}
```

---

## 使用示例

### cURL

```bash
# 获取列表
curl -X GET "{{BASE_URL}}/api/v1/{{resource}}" \
  -H "Authorization: Bearer <token>"

# 创建
curl -X POST "{{BASE_URL}}/api/v1/{{resource}}" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'
```

### Python

```python
import requests

BASE_URL = "{{BASE_URL}}"
TOKEN = "<your_token>"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 获取列表
response = requests.get(f"{BASE_URL}/api/v1/{{resource}}", headers=headers)
data = response.json()

# 创建
response = requests.post(
    f"{BASE_URL}/api/v1/{{resource}}",
    headers=headers,
    json={"name": "test"}
)
```
