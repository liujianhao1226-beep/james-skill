# 重构模式手册

## 提取与内联

### Extract Function（提取函数）
将代码块提取为独立函数。

**适用场景**：
- 代码块可以独立命名
- 代码块在多处重复
- 函数过长需要拆分

```python
# Before
def process_order(order):
    # 验证订单
    if not order.items:
        raise ValueError("订单为空")
    if order.total < 0:
        raise ValueError("金额错误")
    
    # 处理支付
    payment = create_payment(order.total)
    payment.process()
    
    # 发送通知
    send_email(order.user, "订单已处理")

# After
def process_order(order):
    validate_order(order)
    process_payment(order)
    notify_user(order)

def validate_order(order):
    if not order.items:
        raise ValueError("订单为空")
    if order.total < 0:
        raise ValueError("金额错误")

def process_payment(order):
    payment = create_payment(order.total)
    payment.process()

def notify_user(order):
    send_email(order.user, "订单已处理")
```

### Extract Variable（提取变量）
将复杂表达式提取为有意义的变量。

```python
# Before
if user.age >= 18 and user.country == "CN" and user.verified:
    allow_purchase()

# After
is_adult = user.age >= 18
is_domestic = user.country == "CN"
is_verified = user.verified
can_purchase = is_adult and is_domestic and is_verified

if can_purchase:
    allow_purchase()
```

### Inline Function（内联函数）
将过于简单的函数内联到调用处。

```python
# Before
def is_adult(age):
    return age >= 18

if is_adult(user.age):
    ...

# After（如果只用一次且足够简单）
if user.age >= 18:
    ...
```

### Extract Class（提取类）
将相关功能提取为新类。

```python
# Before
class Order:
    def __init__(self):
        self.shipping_name = ""
        self.shipping_address = ""
        self.shipping_city = ""
        self.shipping_zip = ""
    
    def get_shipping_label(self):
        return f"{self.shipping_name}\n{self.shipping_address}\n{self.shipping_city} {self.shipping_zip}"

# After
class ShippingInfo:
    def __init__(self, name, address, city, zip_code):
        self.name = name
        self.address = address
        self.city = city
        self.zip_code = zip_code
    
    def get_label(self):
        return f"{self.name}\n{self.address}\n{self.city} {self.zip_code}"

class Order:
    def __init__(self):
        self.shipping = ShippingInfo()
```

---

## 简化条件

### Decompose Conditional（分解条件）
将复杂条件分解为独立函数。

```python
# Before
if date.month >= 6 and date.month <= 8:
    charge = quantity * summer_rate
else:
    charge = quantity * regular_rate

# After
def is_summer(date):
    return 6 <= date.month <= 8

if is_summer(date):
    charge = summer_charge(quantity)
else:
    charge = regular_charge(quantity)
```

### Replace Nested Conditional with Guard Clauses（用卫语句替代嵌套）
用提前返回替代深层嵌套。

```python
# Before
def get_payment_amount(employee):
    if employee.is_retired:
        result = retired_amount()
    else:
        if employee.is_separated:
            result = separated_amount()
        else:
            result = normal_amount()
    return result

# After
def get_payment_amount(employee):
    if employee.is_retired:
        return retired_amount()
    if employee.is_separated:
        return separated_amount()
    return normal_amount()
```

### Replace Conditional with Polymorphism（用多态替代条件）

```python
# Before
def calculate_area(shape):
    if shape.type == "circle":
        return 3.14 * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height
    elif shape.type == "triangle":
        return 0.5 * shape.base * shape.height

# After
class Circle:
    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle:
    def area(self):
        return self.width * self.height

class Triangle:
    def area(self):
        return 0.5 * self.base * self.height
```

---

## 移动特性

### Move Function（移动函数）
将函数移到更合适的类。

```python
# Before - 函数在错误的类中
class Account:
    def overdraft_charge(self):
        if self.account_type.is_premium:
            return 10
        return 20

# After - 移到 AccountType
class AccountType:
    def overdraft_charge(self):
        if self.is_premium:
            return 10
        return 20

class Account:
    def overdraft_charge(self):
        return self.account_type.overdraft_charge()
```

### Split Loop（拆分循环）
将处理多个事务的循环拆分。

```python
# Before
total_salary = 0
youngest_age = float('inf')
for person in people:
    total_salary += person.salary
    if person.age < youngest_age:
        youngest_age = person.age

# After
total_salary = sum(p.salary for p in people)
youngest_age = min(p.age for p in people)
```

---

## 数据组织

### Replace Magic Number with Constant（用常量替代魔法数字）

```python
# Before
if speed > 120:
    issue_ticket()

# After
SPEED_LIMIT = 120

if speed > SPEED_LIMIT:
    issue_ticket()
```

### Introduce Parameter Object（引入参数对象）

```python
# Before
def amount_invoiced(start_date, end_date):
    ...
def amount_received(start_date, end_date):
    ...

# After
@dataclass
class DateRange:
    start: date
    end: date

def amount_invoiced(date_range: DateRange):
    ...
def amount_received(date_range: DateRange):
    ...
```
