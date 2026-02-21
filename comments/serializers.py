from rest_framework import serializers
from .models import Comment
import bleach
from rest_captcha.serializers import RestCaptchaSerializer

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField(read_only=True)
    
    captcha_key = serializers.CharField(write_only=True, required=True)
    captcha_value = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'username', 'email', 'homepage', 'text', 'image', 'text_file', 'created_at', 'replies', 'captcha_key', 'captcha_value']

    def get_replies(self, obj):
        # Рекурсивный вызов для лесенки
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def validate_text(self, value):
        # Защита от XSS
        allowed_tags = ['a', 'code', 'i', 'strong']
        # Обязательно разрешаем атрибуты для ссылок
        allowed_attrs = {'a': ['href', 'title']}
        clean_text = bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)
        return clean_text

    def validate(self, data):
        # Валидация капчи через библиотеку
        captcha_serializer = RestCaptchaSerializer(data={
            'captcha_key': data.get('captcha_key'),
            'captcha_value': data.get('captcha_value')
        })
        captcha_serializer.is_valid(raise_exception=True)

        # Удаление поля капчи
        data.pop('captcha_key', None)
        data.pop('captcha_value', None)
            
        return data