from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_at', 'parent')
    search_fields = ('username', 'email', 'text')
    list_filter = ('created_at', 'username')
    readonly_fields = ('created_at',)