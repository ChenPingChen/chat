from django.db import models
from django.utils import timezone
from data_manager.models import ViolationEvent
import uuid


class ChatSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['last_activity'])
        ]

class SearchHistory(models.Model):
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    query_text = models.TextField()
    query_embedding = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at'])
        ]

class SearchResult(models.Model):
    result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_history = models.ForeignKey(SearchHistory, on_delete=models.CASCADE)
    violation_event = models.ForeignKey(ViolationEvent, on_delete=models.CASCADE)
    similarity_score = models.FloatField()
    rank = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['similarity_score']),
            models.Index(fields=['rank'])
        ]