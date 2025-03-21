# ملف: api_failover/core.py
import time
import logging
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Optional, List, Union

# إعداد التسجيل
logger = logging.getLogger("api_failover")

class APIFailoverSystem:
    """
    نظام API مع آلية التبديل التلقائي بين خدمات متعددة
    يحاول الاتصال عدة مرات بفاصل زمني محدد قبل التبديل إلى النظام التالي
    """
    
    def __init__(self, services: Optional[List[Dict[str, str]]] = None, 
                 max_retries: int = 5, retry_delay: float = 0.5,
                 timeout: int = 3, log_level: int = logging.INFO):
        """
        تهيئة نظام التبديل التلقائي للـ API
        
        :param services: قائمة بالخدمات، كل خدمة هي قاموس يحتوي على 'name' و 'url'
                        مثال: [{"name": "Flask", "url": "http://localhost:5000/api"}]
        :param max_retries: عدد المحاولات لكل خدمة قبل الانتقال للتالية
        :param retry_delay: الوقت بالثواني بين كل محاولة
        :param timeout: مهلة الطلب بالثواني
        :param log_level: مستوى التسجيل
        """
        # قائمة افتراضية بالخدمات إذا لم يتم تقديم قائمة
        if services is None:
            self.services = [
                {"name": "Flask", "url": "http://localhost:5000/api"},
                {"name": "FastAPI", "url": "http://localhost:8000/api"},
                {"name": "Django", "url": "http://localhost:8080/api"},
            ]
        else:
            self.services = services
            
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # إعداد التسجيل
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        logger.setLevel(log_level)
    
    def _make_request(self, service: Dict[str, str], endpoint: str, method: str = "GET", 
                     data: Optional[Dict[str, Any]] = None, 
                     headers: Optional[Dict[str, str]] = None,
                     files: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """
        إجراء طلب API إلى الخدمة المحددة مع محاولات إعادة
        
        :param service: معلومات الخدمة (الاسم و URL)
        :param endpoint: نقطة النهاية المطلوبة
        :param method: طريقة HTTP (GET، POST، إلخ)
        :param data: البيانات المرسلة في الطلب
        :param headers: رؤوس HTTP
        :param files: ملفات مرفقة
        :param params: معلمات الاستعلام
        :return: كائن الاستجابة أو None في حالة الفشل
        """
        url = f"{service['url']}/{endpoint.lstrip('/')}"
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"محاولة {attempt} للاتصال بـ {service['name']} على {url}")
                
                kwargs = {
                    "headers": headers,
                    "timeout": self.timeout,
                    "params": params
                }
                
                if method.upper() == "GET":
                    response = requests.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, json=data, files=files, **kwargs)
                elif method.upper() == "PUT":
                    response = requests.put(url, json=data, **kwargs)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, **kwargs)
                elif method.upper() == "PATCH":
                    response = requests.patch(url, json=data, **kwargs)
                else:
                    logger.error(f"طريقة HTTP غير مدعومة: {method}")
                    return None
                
                if response.status_code < 400:
                    logger.info(f"نجحت المحاولة {attempt} مع {service['name']}")
                    return response
                
                logger.warning(f"فشلت المحاولة {attempt} مع {service['name']}: رمز الحالة {response.status_code}")
                
            except RequestException as e:
                logger.warning(f"فشلت المحاولة {attempt} مع {service['name']}: {str(e)}")
            
            if attempt < self.max_retries:
                logger.info(f"الانتظار {self.retry_delay} ثانية قبل المحاولة التالية")
                time.sleep(self.retry_delay)
        
        logger.error(f"فشلت جميع المحاولات ({self.max_retries}) للاتصال بـ {service['name']}")
        return None
    
    def make_request(self, endpoint: str, method: str = "GET", 
                    data: Optional[Dict[str, Any]] = None, 
                    headers: Optional[Dict[str, str]] = None,
                    files: Optional[Dict[str, Any]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    return_raw_response: bool = False) -> Optional[Union[Dict[str, Any], requests.Response]]:
        """
        محاولة إجراء طلب API على جميع الخدمات المتاحة حتى النجاح
        
        :param endpoint: نقطة النهاية المطلوبة
        :param method: طريقة HTTP (GET، POST، إلخ)
        :param data: البيانات المرسلة في الطلب
        :param headers: رؤوس HTTP
        :param files: ملفات مرفقة
        :param params: معلمات الاستعلام
        :param return_raw_response: إرجاع كائن الاستجابة الأصلي بدلاً من القاموس
        :return: البيانات المستجابة أو كائن الاستجابة أو None في حالة فشل جميع الخدمات
        """
        for service in self.services:
            logger.info(f"محاولة استخدام خدمة {service['name']}")
            response = self._make_request(service, endpoint, method, data, headers, files, params)
            
            if response is not None:
                logger.info(f"نجح الطلب باستخدام {service['name']}")
                
                if return_raw_response:
                    return response
                
                try:
                    return {
                        "service_used": service['name'],
                        "status_code": response.status_code,
                        "data": response.json() if response.content else None
                    }
                except ValueError:
                    return {
                        "service_used": service['name'],
                        "status_code": response.status_code,
                        "data": response.text
                    }
        
        logger.error("فشلت جميع الخدمات في معالجة الطلب")
        return None
    
    def add_service(self, name: str, url: str) -> None:
        """
        إضافة خدمة جديدة إلى قائمة الخدمات
        
        :param name: اسم الخدمة
        :param url: عنوان URL للخدمة
        """
        self.services.append({"name": name, "url": url})
        logger.info(f"تمت إضافة خدمة جديدة: {name} على {url}")
    
    def remove_service(self, name: str) -> bool:
        """
        إزالة خدمة من قائمة الخدمات باستخدام اسمها
        
        :param name: اسم الخدمة المراد إزالتها
        :return: True إذا تمت الإزالة بنجاح، False إذا لم يتم العثور على الخدمة
        """
        for i, service in enumerate(self.services):
            if service["name"] == name:
                self.services.pop(i)
                logger.info(f"تمت إزالة الخدمة: {name}")
                return True
        
        logger.warning(f"لم يتم العثور على الخدمة: {name}")
        return False