from rest_framework import serializers
from .models import ChatSession, SearchHistory, SearchResult
from data_manager.models import ViolationEvent

class ViolationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationEvent
        fields = '__all__'

class SearchResultSerializer(serializers.ModelSerializer):
    violation_event = ViolationEventSerializer()
    
    class Meta:
        model = SearchResult
        fields = ['result_id', 'violation_event', 'similarity_score', 'rank']