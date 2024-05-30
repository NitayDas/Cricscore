from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *
from .models import *
from django.utils import timezone
from datetime import datetime,timedelta
import requests


def home(request):
    return render(request, 'Home/home.html')



class MatchesList(APIView):
    def get(self, request):
        today=timezone.now()
        five_days_earlier = today - timedelta(days=8)
        seven_days_later = today + timedelta(days=7)
        matches=Matches.objects.filter(start_date__date__range=(five_days_earlier.date(),seven_days_later.date()))
        serializer = MatchesSerializer(matches,many=True)
        return Response(serializer.data)
    
# class MatchDetails(APIView):
#     def get(self,request,match_id):
#         # print(match_id)
#         match = Matches.objects.get(match_id=match_id)
#         innings_id = match.innings_id
#         # print(innings_id)
#         oversummary = OverSummary.objects.filter(match_id=match_id,InningsId=innings_id)
#         serializer = OverSummarySerializer(oversummary,many=True)
#         return Response(serializer.data)


# class ScoreboardDetails(APIView):
#     def get(self,request,match_id):
#         try:
#             match = Matches.objects.get(match_id=match_id)
            
#         except Matches.DoesNotExist:
#             return Response({"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         scoreboard = Scoreboard.objects.filter(match=match)
        
#         if not scoreboard.exists():
#             return Response({"error": "No scoreboards found for this match"}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = ScoreboardSerializer(scoreboard, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
        
    
class overSummary_and_Scoreboard(APIView):
    def get(self, request, match_id):
        
        try:
             match = Matches.objects.get(match_id=match_id)
             
        except Matches.DoesNotExist:
            return Response({"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch and serialize scoreboard data
        scoreboard = Scoreboard.objects.filter(match=match)
        scoreboard_serializer = ScoreboardSerializer(scoreboard, many=True)
        
        # Fetch and serialize over summary data
        oversummary = OverSummary.objects.filter(match_id=match_id, InningsId=match.innings_id)
        oversummary_serializer = OverSummarySerializer(oversummary, many=True)
        
        # Combine all serialized data into one response
        response_data = {
            "scoreboard": scoreboard_serializer.data,
            "oversummary": oversummary_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        


