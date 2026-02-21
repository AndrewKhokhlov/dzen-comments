from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from rest_framework import generics, pagination, filters
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Comment
from .serializers import CommentSerializer
from .tasks import resize_image_task


class CommentPagination(pagination.PageNumberPagination):
    page_size = 25 # Ровно 25 комментариев на страницу по ТЗ
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentListCreateView(generics.ListCreateAPIView):
    # Фильтр главных комментов
    queryset = Comment.objects.filter(parent__isnull=True).prefetch_related('replies')
    serializer_class = CommentSerializer
    
    pagination_class = CommentPagination 

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']

    # Кэш GET-запросы на 15 секунд
    @method_decorator(cache_page(15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Сохранение коммента в БД
        comment = serializer.save()
        
        # Отправление картинки в Celery, все в фоне
        if comment.image:
            resize_image_task.delay(comment.id)
            
        # Отправлени коммента через WebSockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments_group", 
            {
                "type": "send_comment",
                "comment": serializer.data
            }
        )

class IndexView(TemplateView):
    template_name = 'index.html'