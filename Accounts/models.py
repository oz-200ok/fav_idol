from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 사용자 관리자 클래스
class UserManager(BaseUserManager):
    def create_user(self, email, username, name, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다')
        if not username:
            raise ValueError('닉네임은 필수입니다')
        if not name:
            raise ValueError('이름은 필수입니다')
            
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            **extra_fields
        )
        if extra_fields.get('is_social', False):
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, username, name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, username, name, password, **extra_fields)

# 사용자 모델
class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)  # 이메일 인증 여부
    name = models.CharField(max_length=20)
    username = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_social = models.BooleanField(default=False)
    social_login = models.CharField(max_length=15, null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    def __str__(self):
        return self.email
        
    class Meta:
        db_table = 'user'
