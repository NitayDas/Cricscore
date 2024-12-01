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
        fields = ['id','event','parent' ,'user', 'content', 'created_at', 'replies', 'parent_user','likes','liked_by']

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
    
    
class topCommentSerializer(serializers.ModelSerializer):
    match_id = serializers.SerializerMethodField()  # Include match_id
    over_num = serializers.SerializerMethodField()  # Include over_summary_id
    InningsId = serializers.SerializerMethodField()
    parent_user = serializers.SerializerMethodField()
    

    class Meta:
        model = Comment
        fields = [
            'id',
            'event',
            'user',
            'content',
            'created_at',
            'parent_user',
            'likes',
            'liked_by',
            'match_id', 
            'InningsId',
            'over_num', 
        ]

    def get_parent_user(self, obj):
        # Fetch the parent user's details if a parent comment exists
        if obj.parent and obj.parent.user:
            return {
                'name': obj.parent.user.get('name'),
                'email': obj.parent.user.get('email')
            }
        return None

    def get_match_id(self, obj):
        if hasattr(obj.event, 'match_id'):
            return obj.event.match_id
        return None

    def get_over_num(self, obj):
        return obj.event.OverNum if obj.event else None
    
    def get_InningsId(self, obj):
        return obj.event.InningsId if obj.event else None
    

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'   