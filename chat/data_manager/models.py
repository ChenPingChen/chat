from django.db import models
from django.utils import timezone
from pgvector.django import VectorField
import uuid

class ViolationEvent(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    violation_type = models.CharField(max_length=50)
    details = models.TextField()
    image_url = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    camera_id = models.CharField(max_length=50)
    scene_id = models.CharField(max_length=50)
    image_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    processed_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', '待處理'),
            ('PROCESSING', '處理中'),
            ('COMPLETED', '已完成'),
            ('FAILED', '失敗')
        ],
        default='PENDING'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['violation_type']),
            models.Index(fields=['start_time']),
            models.Index(fields=['camera_id']),
            models.Index(fields=['processed_status'])
        ]

class PersonInfo(models.Model):
    violation_event = models.ForeignKey(ViolationEvent, on_delete=models.CASCADE)
    person_role = models.CharField(max_length=100)
    person_id = models.CharField(max_length=50)
    equipment = models.JSONField()

class ConstructionVehicle(models.Model):
    violation_event = models.ForeignKey(ViolationEvent, on_delete=models.CASCADE, related_name='construction_vehicles')
    vehicle_name = models.CharField(max_length=100, blank=True)
    vehicle_state = models.CharField(max_length=100, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['vehicle_name']),
            models.Index(fields=['vehicle_state'])
        ]

class Device(models.Model):
    violation_event = models.ForeignKey(ViolationEvent, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=100, blank=True)
    device_state = models.CharField(max_length=100, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['device_name']),
            models.Index(fields=['device_state'])
        ]

class VectorStore(models.Model):
    vector_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    violation_event = models.OneToOneField(
        ViolationEvent, 
        on_delete=models.CASCADE,
        related_name='vector_data'
    )
    image_embedding = VectorField(dimensions=768)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at'])
        ]