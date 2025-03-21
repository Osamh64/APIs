# ملف: examples/basic_usage.py
import logging
from APIs import APIFailoverSystem

# إعداد التسجيل للمثال
logging.basicConfig(level=logging.INFO)

def demo_api_failover():
    # إنشاء نظام التبديل التلقائي مع خدمات مخصصة
    services = [
        {"name": "PrimaryAPI", "url": "http://localhost:5000/api"},
        {"name": "SecondaryAPI", "url": "http://localhost:8000/api"},
        {"name": "BackupAPI", "url": "http://localhost:8080/api"}
    ]
    
    api_system = APIFailoverSystem(
        services=services,
        max_retries=5,
        retry_delay=0.5
    )
    
    # مثال 1: طلب GET بسيط
    print("\n=== مثال 1: طلب GET بسيط ===")
    result = api_system.make_request("users")
    if result:
        print(f"نجح الطلب باستخدام خدمة: {result['service_used']}")
        print(f"رمز الحالة: {result['status_code']}")
        print(f"البيانات: {result['data']}")
    else:
        print("فشلت جميع الخدمات")
    
    # مثال 2: طلب POST مع بيانات
    print("\n=== مثال 2: طلب POST مع بيانات ===")
    data = {
        "username": "user123",
        "email": "user@example.com",
        "fullname": "Test User"
    }
    result = api_system.make_request("users", method="POST", data=data)
    if result:
        print(f"نجح الطلب باستخدام خدمة: {result['service_used']}")
        print(f"رمز الحالة: {result['status_code']}")
        print(f"البيانات: {result['data']}")
    else:
        print("فشلت جميع الخدمات")
    
    # مثال 3: إضافة خدمة جديدة وإزالة خدمة
    print("\n=== مثال 3: إدارة الخدمات ===")
    api_system.add_service("EmergencyAPI", "http://localhost:9000/api")
    print("تمت إضافة خدمة EmergencyAPI")
    
    removed = api_system.remove_service("BackupAPI")
    print(f"{'تمت' if removed else 'فشلت'} إزالة خدمة BackupAPI")
    
    # عرض الخدمات الحالية
    print("\nالخدمات الحالية:")
    for i, service in enumerate(api_system.services, 1):
        print(f"{i}. {service['name']}: {service['url']}")

if __name__ == "__main__":
    demo_api_failover()