import bleach
from PIL import Image
from django.db import models
from django.core.validators import RegexValidator

class Comment(models.Model):
    # цифры и буквы латиницы
    alphanumeric_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]+$',
        message='Имя пользователя может содержать только латинские буквы и цифры.'
    )
    
    username = models.CharField(max_length=100, validators=[alphanumeric_validator])
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True) 
    text = models.TextField()
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    text_file = models.FileField(upload_to='text_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Сортировка по умолчанию
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.created_at}"

    def save(self, *args, **kwargs):
        # Защита от XSS
        allowed_tags = ['a', 'code', 'i', 'strong']
        allowed_attrs = {'a': ['href', 'title']}
        self.text = bleach.clean(self.text, tags=allowed_tags, attributes=allowed_attrs, strip=True)

        # Сначало в базу сохр потом на страницу
        super().save(*args, **kwargs)

        # Не более 320x240
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 240 or img.width > 320:
                output_size = (320, 240)
                img.thumbnail(output_size)
                img.save(self.image.path)