# API Failover System

مكتبة بايثون للتبديل التلقائي بين خدمات API متعددة مع آلية إعادة المحاولة. المكتبة تتيح لك تحديد مجموعة من خدمات API وتحاول الاتصال بكل خدمة بعدد محدد من المحاولات قبل الانتقال إلى الخدمة التالية.

## التثبيت

```bash
pip install api-failover
```

## الاستخدام الأساسي

```python
from api_failover import APIFailoverSystem

# إنشاء نظام التبديل التلقائي باستخدام الإعدادات الافتراضية
# (Flask -> FastAPI -> Django)
api_system = APIFailoverSystem()

# إجراء طلب GET
result = api_system.make_request("users")

if result:
    print(f"نجح الطلب باستخدام خدمة {result['service_used']}")
    print(f"البيانات المستلمة: {result['data']}")
else:
    print("فشلت جميع الخدمات")
```

## خيارات متقدمة

### تحديد الخدمات المخصصة

```python
from api_failover import APIFailoverSystem

services = [
    {"name": "MainAPI", "url": "https://api.example.com/v1"},
    {"name": "BackupAPI", "url": "https://backup-api.example.com/v1"},
    {"name": "FallbackAPI", "url": "https://fallback.example.com/v1"}
]

api_system = APIFailoverSystem(
    services=services,
    max_retries=3,             # عدد محاولات لكل خدمة
    retry_delay=1.0,           # وقت الانتظار بين المحاولات (بالثواني)
    timeout=5,                 # مهلة الطلب (بالثواني)
    log_level=logging.DEBUG    # مستوى التسجيل
)
```

### إجراء طلبات متنوعة

```python
# إجراء طلب POST مع بيانات JSON
data = {"name": "John", "email": "john@example.com"}
result = api_system.make_request("users", method="POST", data=data)

# إرفاق ملفات
with open("document.pdf", "rb") as file:
    files = {"document": file}
    result = api_system.make_request("upload", method="POST", files=files)

# إضافة رؤوس مخصصة
headers = {"Authorization": "Bearer token123"}
result = api_system.make_request("secured-endpoint", headers=headers)

# إرجاع كائن الاستجابة الخام
response = api_system.make_request("data", return_raw_response=True)
if response:
    # العمل مباشرة مع كائن الاستجابة
    print(response.status_code)
    print(response.headers)
    print(response.json())
```

### إدارة الخدمات

```python
# إضافة خدمة جديدة
api_system.add_service("EmergencyAPI", "https://emergency.example.com/api")

# إزالة خدمة
api_system.remove_service("BackupAPI")
```

## المميزات

- آلية إعادة المحاولة مع فترة انتظار قابلة للتخصيص
- تبديل تلقائي بين الخدمات المتعددة
- دعم لجميع طرق HTTP الشائعة (GET, POST, PUT, DELETE, PATCH)
- تسجيل شامل للأحداث
- تخصيص سهل للإعدادات
- دعم للملفات المرفقة
- إمكانية إضافة وإزالة الخدمات ديناميكيًا

## المتطلبات

- Python 3.6+
- مكتبة Requests# APIs
