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


        
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()  # Fetch replies recursively
    parent_user = serializers.SerializerMethodField()  # Include parent user in the reply

    class Meta:
        model = Comment
        fields = ['id','event','parent' ,'user', 'content', 'created_at', 'replies', 'parent_user']

    def get_replies(self, obj):
        replies = obj.replies.all()
        if replies.exists():
            serializer = CommentSerializer(replies, many=True, context=self.context)
            for item in serializer.data:
                item.pop('event')  
                item.pop('parent') 
            return serializer.data
        return None

    def get_parent_user(self, obj):
        # Fetch the parent user's details if a parent comment exists
        if obj.parent and obj.parent.user:
            return {
                'name': obj.parent.user.get('name'),
                'email': obj.parent.user.get('email')
            }
        return None
    