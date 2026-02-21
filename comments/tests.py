from django.test import TestCase
from rest_framework.test import APIClient
from .models import Comment

class CommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.comment = Comment.objects.create(
            username="TestUser",
            email="test@example.com",
            text="Обычный безопасный текст"
        )

    def test_comment_creation(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.username, "TestUser")

    def test_xss_protection(self):
        bad_comment = Comment.objects.create(
            username="Hacker",
            email="hacker@evil.com",
            text="<script>alert('XSS')</script>Опасный код"
        )
        
        self.assertNotIn("<script>", bad_comment.text)
        self.assertIn("Опасный код", bad_comment.text)

    def test_api_get_comments(self):
        response = self.client.get('/api/comments/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)