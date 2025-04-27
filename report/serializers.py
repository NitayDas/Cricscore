from rest_framework import serializers 
from .models import MatchCommentStats, TeamCommentStats

class MatchCommentStatsSerializer(serializers.ModelSerializer):
    class Meta: 
        model = MatchCommentStats 
        fields = '__all__'
        
        
class TeamCommentStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCommentStats
        fields = '__all__'