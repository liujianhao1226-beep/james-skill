# 代码异味清单

## 什么是代码异味？

代码异味（Code Smell）是代码中可能存在问题的信号，不一定是 bug，但暗示设计可能需要改进。

---

## 膨胀类异味 (Bloaters)

### 1. 过长函数 (Long Method)
**症状**: 函数超过 20-30 行

**解决方案**:
- Extract Function（提取函数）
- Replace Temp with Query（用查询替代临时变量）
- Decompose Conditional（分解条件）

```python
# 异味信号
def process_order(order):
    # 50+ 行代码...
    pass

# 建议: 拆分为多个小函数
```

### 2. 过大类 (Large Class)
**症状**: 类有太多字段、方法，职责过多

**解决方案**:
- Extract Class（提取类）
- Extract Subclass（提取子类）
- Extract Interface（提取接口）

### 3. 过长参数列表 (Long Parameter List)
**症状**: 函数参数超过 3-4 个

**解决方案**:
- Introduce Parameter Object（引入参数对象）
- Preserve Whole Object（保持对象完整）
- Replace Parameter with Method Call

```python
# 异味
def create_user(name, email, age, city, country, zip_code, phone):
    pass

# 改进
@dataclass
class UserInfo:
    name: str
    email: str
    age: int
    address: Address
    phone: str

def create_user(user_info: UserInfo):
    pass
```

### 4. 数据泥团 (Data Clumps)
**症状**: 相同的数据项总是一起出现

**解决方案**:
- Extract Class（提取类）
- Introduce Parameter Object

```python
# 异味 - 这三个总是一起出现
def set_location(latitude, longitude, altitude):
    pass
def get_distance(lat1, lon1, alt1, lat2, lon2, alt2):
    pass

# 改进
@dataclass
class GeoPoint:
    latitude: float
    longitude: float
    altitude: float

def set_location(point: GeoPoint):
    pass
def get_distance(point1: GeoPoint, point2: GeoPoint):
    pass
```

---

## 滥用面向对象 (OO Abusers)

### 5. Switch 语句 (Switch Statements)
**症状**: 重复的 switch/if-else 链

**解决方案**:
- Replace Conditional with Polymorphism
- Replace Type Code with Subclasses
- 使用策略模式或工厂模式

### 6. 临时字段 (Temporary Field)
**症状**: 对象字段只在某些情况下有值

**解决方案**:
- Extract Class
- Introduce Null Object

### 7. 被拒绝的遗赠 (Refused Bequest)
**症状**: 子类不使用父类的方法或数据

**解决方案**:
- Replace Inheritance with Delegation
- Extract Subclass

---

## 变革阻碍者 (Change Preventers)

### 8. 发散式变化 (Divergent Change)
**症状**: 一个类因多种原因而修改

**解决方案**:
- Extract Class（按职责拆分）

```python
# 异味 - 这个类因为多种原因修改
class Employee:
    def calculate_pay(self): ...      # 薪资规则变化
    def report_hours(self): ...       # 报表格式变化
    def save(self): ...               # 数据库 schema 变化
```

### 9. 散弹式修改 (Shotgun Surgery)
**症状**: 一个改动需要修改多个类

**解决方案**:
- Move Method / Move Field
- Inline Class

### 10. 平行继承体系 (Parallel Inheritance Hierarchies)
**症状**: 添加一个子类需要在另一个继承体系添加对应子类

**解决方案**:
- Move Method / Move Field

---

## 非必要元素 (Dispensables)

### 11. 注释过多 (Comments)
**症状**: 用注释解释难懂的代码

**解决方案**:
- Extract Method（用方法名代替注释）
- Rename Method

```python
# 异味
# 检查用户是否有权限购买酒精饮料
if user.age >= 18 and user.country == "CN":
    ...

# 改进 - 代码自解释
if user.can_purchase_alcohol():
    ...
```

### 12. 重复代码 (Duplicated Code)
**症状**: 相同代码出现多处

**解决方案**:
- Extract Method
- Pull Up Method
- Form Template Method

### 13. 冗赘类 (Lazy Class)
**症状**: 类做的事情太少，不值得存在

**解决方案**:
- Inline Class
- Collapse Hierarchy

### 14. 夸夸其谈的未来性 (Speculative Generality)
**症状**: 为"将来可能用到"而创建的抽象

**解决方案**:
- Collapse Hierarchy
- Inline Class
- Remove Parameter

### 15. 死代码 (Dead Code)
**症状**: 不再使用的代码

**解决方案**:
- 直接删除

---

## 耦合问题 (Couplers)

### 16. 依恋情结 (Feature Envy)
**症状**: 方法更多使用其他类的数据

**解决方案**:
- Move Method

```python
# 异味
class Order:
    def calculate_discount(self):
        # 大量使用 customer 的数据
        if self.customer.loyalty_points > 100:
            if self.customer.member_since < 2020:
                return self.customer.discount_rate * 1.5
        return self.customer.discount_rate

# 改进 - 移到 Customer 类
class Customer:
    def calculate_order_discount(self, order):
        ...
```

### 17. 过度亲密 (Inappropriate Intimacy)
**症状**: 类之间过于了解对方的内部细节

**解决方案**:
- Move Method / Move Field
- Hide Delegate
- Replace Inheritance with Delegation

### 18. 消息链 (Message Chains)
**症状**: 连续的方法调用链

```python
# 异味
user.get_department().get_manager().get_email()

# 改进 - 引入委托方法
user.get_manager_email()
```

### 19. 中间人 (Middle Man)
**症状**: 类的方法都是委托给其他类

**解决方案**:
- Remove Middle Man
- Inline Method
