# Jooyar Python SDK

[![PyPI](https://img.shields.io/pypi/v/jouyaar.svg)](https://pypi.org/project/jouyaar/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://pypi.org/project/jouyaar/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<div dir="rtl">

کلاینت رسمی پایتون برای API **جویار**، سرویس جست‌وجوی هوشمندی که نتایج ده‌ها ارائه‌دهندهٔ ایرانی را
یک‌جا مقایسه می‌کند. با این SDK می‌توانید در پرواز، اقامتگاه، اتوبوس، قطار، کالا و اینترنت جست‌وجو کنید
و ارزان‌ترین و بهترین گزینه‌ها را به‌صورت رتبه‌بندی‌شده دریافت کنید — بدون آن‌که لازم باشد سایت‌ها را
یکی‌یکی بگردید. کافی است یک فراخوانی ساده در کد خود بزنید و نتیجه را بگیرید.

## نصب

</div>

```bash
pip install jouyaar
# یا با uv:
uv add jouyaar
```

<div dir="rtl">

## شروع سریع

</div>

```python
from jouyaar import Jooyaar

client = Jooyaar(api_key="sk_live_…")   # یا متغیر محیطی JOUYAAR_API_KEY

res = client.search(category="flight", prompt="ارزان‌ترین پرواز تهران به مشهد فردا صبح")
for q in res.quotes:
    print(q.provider, f"{q.price_toman:,} تومان", q.plan_name)
```

<div dir="rtl">

## امکانات

- کلاینت هم‌زمان (`Jooyaar`) و ناهم‌زمان (`AsyncJooyaar`)
- جست‌وجوی ساختاریافته (`params=`) یا با زبان طبیعی (`prompt=`)
- خطاهای تایپ‌دار و retry خودکار با backoff روی خطاهای `429/5xx`
- کاملاً type-hinted، با مدل‌های Pydantic

## مستندات

کلید API بگیرید و مستندات کامل را در **[developers.jouyaar.ir](https://developers.jouyaar.ir)** بخوانید.

با مجوز MIT منتشر شده است.

</div>
