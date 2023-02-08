import jwt
from datetime import datetime, timedelta

from django.conf import settings

from django.contrib.auth.models import	AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, username, password):

        if not email:
            raise ValueError("Email must be specified")

        if not username:
            raise ValueError("Username must be specified")

        if not password:
            raise ValueError("Password must be specified")
        
        user = self.model(
            email=email,
            username=username,
            password=password,
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password):
    
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser):
    
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(verbose_name='username', max_length=60, db_index=True)
    last_request = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        
            return self.email

    def _generate_jwt_token(self):
        
        token_lifetime = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(token_lifetime.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    @property
    def token(self):

        return self._generate_jwt_token()
    

class Post(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='Like', related_name='likes')
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')