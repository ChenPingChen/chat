from rest_framework import serializers
from .models import ViolationEvent, PersonInfo

class PersonInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonInfo
        fields = ['person_role', 'person_id', 'equipment']

class ViolationEventSerializer(serializers.ModelSerializer):
    person_info = PersonInfoSerializer(source='personinfo_set', many=True, read_only=True)
    
    class Meta:
        model = ViolationEvent
        fields = [
            'event_id', 'violation_type', 'details', 'image_url',
            'start_time', 'end_time', 'camera_id', 'scene_id',
            'image_path', 'created_at', 'processed_status',
            'person_info'
        ]
        read_only_fields = ['event_id', 'created_at', 'processed_status']