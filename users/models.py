#users/models.py
from django.db import models
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image

class UserProfile(AbstractUser):
    # Никнейм и email уже есть в стандартной модели User
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=255, unique=True,null=True)
    
    # Хэш-кошельков (список)
    wallet_hashes = models.JSONField(default=list, blank=True, null=True)  # Изменено: добавлено null=True
    
    wallet_credentials = models.JSONField(default=list, blank=True, null=True)  # Изменено: добавлено null=True
    
    # Информация о пользователе
    bio = models.TextField(blank=True, null=True)
    
    # Дата регистрации
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Профильная картинка
    profile_image = models.ImageField(
        default='user_images/avatar.jpg',
        upload_to='user_images',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # Сохраняем пользователя
        super().save(*args, **kwargs)

        # Обрабатываем изображение
        if self.profile_image:
            img = Image.open(self.profile_image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)

    def __str__(self):
        return self.nickname

class UserBlock(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallets"
    )
    curlid = models.CharField(max_length=255)
    hash = models.CharField(max_length=255, unique=True)  # Wallet hash, unique to avoid duplicates
    coins = models.IntegerField()

    def __str__(self):
        user_info = f"User {self.user.nickname}" if self.user else "Unlinked Wallet"
        return f"{user_info} - Wallet {self.hash[:6]} - Coins: {self.coins}"


class BlockActive(models.Model):
    prev_hash = models.CharField(max_length=255)
    current_hash = models.CharField(max_length=255)
    is_genesis = models.BooleanField()
    valid_count = models.IntegerField()

    def __str__(self):
        return f"Block {self.current_hash[:6]} - Valid Count: {self.valid_count}"


class BlockActiveDataJson(models.Model):
    block = models.ForeignKey(BlockActive, on_delete=models.CASCADE, related_name="data_json")
    hash = models.CharField(max_length=255)
    message = models.TextField(null=True, blank=True)
    
    # Связываем кошельки отправителя и получателя с UserBlock
    to_wallet = models.ForeignKey(
        UserBlock, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="received_transactions"
    )
    from_wallet = models.ForeignKey(
        UserBlock, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="sent_transactions"
    )
    
    prev_hash = models.CharField(max_length=255)
    type_task = models.CharField(max_length=50)
    count_coins = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"DataJson Entry in Block {self.block.current_hash[:6]}"