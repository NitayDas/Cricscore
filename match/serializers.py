from rest_framework import serializers
from .models import *

class MatchesSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Matches
        fields = '__all__'
        
class OverSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OverSummary
        fields = '__all__'

    