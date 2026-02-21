from celery import shared_task
from PIL import Image
from .models import Comment

@shared_task
def resize_image_task(comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)

        if not comment.image:
            return

        # Pillow с защитой от битых файлов
        try:
            img = Image.open(comment.image.path)
            
            # Нее более 320x240
            if img.height > 240 or img.width > 320:
                output_size = (320, 240)
                img.thumbnail(output_size)
                img.save(comment.image.path)
        except Exception as e:
            print(f"Ошибка при обработке изображения для комментария {comment_id}: {e}")
            
    except Comment.DoesNotExist:
        pass