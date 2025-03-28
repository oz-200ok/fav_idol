# Django 기본 설정
DEBUG = False
ALLOWED_HOSTS = ["ilog.giize.com", "localhost"]

# 메일 URL
MAIL_URL = "https://ilog.giize.com/ilog/account"

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://dev.i-log.p-e.kr",
    "https://i-log.p-e.kr",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF 설정
CSRF_TRUSTED_ORIGINS = ["https://ilog.giize.com", "https://*.ilog.giize.com"]
