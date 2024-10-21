from rest_framework import serializers
from .models import *


class SeriesSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Series
        fields = '__all__'
        
class SeriesMatchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matches
        fields = '__all__'   
          
class MatchesSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Matches
        fields = '__all__'
        
class OverSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OverSummary
        fields = '__all__'
        
class ScoreboardSerializer(serializers.ModelSerializer):
     class Meta:
         model = Scoreboard
         fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'username', 'content', 'created_at']
        
class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True) 
    class Meta:
        model = Comment
        fields = ['id', 'event', 'username', 'content', 'created_at', 'replies']

    