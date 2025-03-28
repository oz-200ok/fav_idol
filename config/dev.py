# Django 기본 설정
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 메일 URL
MAIL_URL = "http://127.0.0.1:8000/ilog/account"

# CORS 설정
CORS_ALLOWED_ORIGINS = ["http://localhost:8000"]
CORS_ALLOW_CREDENTIALS = True

# CSRF 설정
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]