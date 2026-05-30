# Sarmo - Clothing Store Management System

A comprehensive order management and inventory system designed for clothing stores, developed with Streamlit.

## Features

- ✅ **Order Registration** with Persian date
- ✅ **PDF Invoice Export** with Persian font and company logo
- ✅ **Reprint** any previous invoice
- ✅ **CSV Export** of invoices and customer lists
- ✅ **Filter** invoices by customer, registrar
- ✅ **Admin Panel** with system logs
- ✅ **Sales Chart** by customer
- ✅ **Inventory Management** with manual editing and stock recharge
- ✅ **Size & Color** selection for products (T-shirt, Hoodie, Sweater, Other)
- ✅ **Automatic stock deduction** after each order

## Product Types

- T-shirt
- Hoodie
- Sweater
- Other

## Sizes

S, M, L, XL, XXL

## Colors

Black, White, Light Blue, Dark Blue, Light Green, Dark Green, Cream, Red, Gray, Brown, Purple, Brown Stonewash, Gray Stonewash, Orange

## Installation

### Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py

Deploy on Liara

    Create a disk named visitor-data mounted to /app/data

    Deploy using drag & drop or GitHub Actions

File Structure
text

├── app.py
├── Dockerfile
├── liara.json
├── requirements.txt
├── logo.png (optional)
└── README.md

Data Persistence

All data is stored in the data/ folder and persists between restarts when deployed with a Liara disk.
License

Private project - All rights reserved.
سرمد - سیستم مدیریت فروشگاه لباس

سیستم جامع ثبت سفارش و مدیریت انبار برای فروشگاه‌های لباس، توسعه یافته با Streamlit
قابلیت‌ها

    ✅ ثبت سفارش با تاریخ شمسی

    ✅ خروجی PDF فاکتور با فونت فارسی و لوگو شرکت

    ✅ چاپ مجدد هر فاکتور قدیمی

    ✅ خروجی CSV فاکتورها و لیست مشتریان

    ✅ فیلتر روی فاکتورها (مشتری، ثبت‌کننده)

    ✅ پنل ادمین با لاگ سیستم

    ✅ نمودار فروش به تفکیک مشتری

    ✅ مدیریت انبار با قابلیت ویرایش دستی و شارژ مجدد

    ✅ انتخاب سایز و رنگ برای محصولات (تیشرت، هودی، دورس، متفرقه)

    ✅ کاهش خودکار موجودی پس از هر سفارش

انواع محصولات

    تیشرت

    هودی

    دورس

    متفرقه

سایزها

S, M, L, XL, XXL
رنگ‌ها

مشکی، سفید، آبی کمرنگ، آبی پررنگ، سبز کمرنگ، سبز پررنگ، کرم، قرمز، طوسی، قهوه‌ای، بنفش، قهوه‌ای سنگشور، طوسی سنگشور، نارنجی

نصب
اجرای محلی
bash

pip install -r requirements.txt
streamlit run app.py

استقرار روی لیارا

    یک دیسک به نام visitor-data با مسیر /app/data بسازید

    با روش کشیدن و رها کردن (Drag & Drop) یا GitHub Actions مستقر کنید

ساختار فایل‌ها
text

├── app.py
├── Dockerfile
├── liara.json
├── requirements.txt
├── logo.png (اختیاری)
└── README.md

نگهداری داده‌ها

تمام داده‌ها در پوشه data/ ذخیره می‌شوند و با استفاده از دیسک لیارا بین ری‌استارت‌ها حفظ می‌شوند.
مجوز

پروژه خصوصی - کلیه حقوق محفوظ است.
