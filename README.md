# Hướng dẫn sử dụng project

update: 14/3/2022

## Clone Project

Thực hiện việc clone project như bình thường, clone nhánh `develop` để có được code mới nhất.

## Setup

### Cài đặt các package

Bạn gõ câu lệnh sau để tiến hành cài đặt hết những package cần có

```
pip install -r requirement
```

Khi đó tất cả các package sẽ được install đầy đủ. Các bạn nên chạy nó trong **vitual env** nhé

## Chạy dự án

Để chạy được dự án bạn chỉ cần sử dụng câu lệnh

```
python manage.py runserver
```

*Lưu ý khi check local, cần setup 1 số điểm

1. Tạo file `.env` và chỉnh sửa như sau
   ```
   SECRET_KEY=django-insecure-ckzjk(yd8)coxlm2qf#^^h%4m=7k21l7_=enq9^8u&^_@ztv0-
   DATABASE_NAME=<tên db>
   DATABASE_USER=<username>
   DATABASE_PASS=<password>
   DB_HOST=localhost
   DB_PORT=3306
   DEBUG=True
   ```
2. Chạy lệnh : python manage.py makemigrations
3. Chạy lệnh : python manage.py migrate 
4. Chạy lệnh : python manage.py createsuperuser để tạo tài khoản admin 
   email: bookmeeting@gmail.com
   password: gõ thôi không cần nhìn
5. Khởi động server: python manage.py runserver

<!-- create Dockerfile and docker-compose.yml
docker-compose build
docker-compose up -->

