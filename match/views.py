from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MatchesSerializer
from .models import *
from django.utils import timezone
from datetime import datetime,timedelta
import requests



def home(request):
    return render(request, 'Home/home.html')

class MatchesList(APIView):
    def get(self, request):
        today=timezone.now()
        five_days_earlier = today - timedelta(days=5)
        seven_days_later = today + timedelta(days=7)
        matches=Matches.objects.filter(start_date__date__range=(five_days_earlier.date(),seven_days_later.date()))
        serializer = MatchesSerializer(matches,many=True)
        return Response(serializer.data)
        


