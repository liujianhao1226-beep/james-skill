# 安全检查清单

## OWASP Top 10 检查项

### 1. 注入攻击 (Injection)
- [ ] SQL 查询是否使用参数化查询
- [ ] 命令执行是否过滤用户输入
- [ ] LDAP/XPath 查询是否安全

### 2. 身份认证失效 (Broken Authentication)
- [ ] 密码是否明文存储
- [ ] Session 管理是否安全
- [ ] 是否有暴力破解防护

### 3. 敏感数据泄露 (Sensitive Data Exposure)
- [ ] 敏感数据是否加密传输 (HTTPS)
- [ ] 密钥/Token 是否硬编码
- [ ] 日志是否记录敏感信息

### 4. XXE (XML External Entities)
- [ ] XML 解析是否禁用外部实体
- [ ] DTD 是否禁用

### 5. 访问控制失效 (Broken Access Control)
- [ ] 是否验证用户权限
- [ ] 是否存在 IDOR 漏洞
- [ ] 目录遍历是否防护

### 6. 安全配置错误 (Security Misconfiguration)
- [ ] Debug 模式是否关闭
- [ ] 默认账户是否删除
- [ ] 错误信息是否泄露堆栈

### 7. XSS (Cross-Site Scripting)
- [ ] 用户输入是否转义
- [ ] CSP 是否配置
- [ ] Cookie 是否设置 HttpOnly

### 8. 不安全的反序列化 (Insecure Deserialization)
- [ ] 是否接受不可信数据的反序列化
- [ ] 是否验证序列化数据的完整性

### 9. 使用含有已知漏洞的组件
- [ ] 依赖是否有已知 CVE
- [ ] 依赖版本是否及时更新

### 10. 日志和监控不足
- [ ] 关键操作是否记录日志
- [ ] 异常是否有告警

## 快速检查命令

```bash
# 搜索硬编码密钥
grep -rn "password\|secret\|api_key\|token" --include="*.py" --include="*.js"

# 搜索 SQL 拼接
grep -rn "execute.*%s\|execute.*+\|execute.*f\"" --include="*.py"
```
