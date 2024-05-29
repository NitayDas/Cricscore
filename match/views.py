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

# Storing OverSummary
# def home(request):
#     from .models import Matches,OverSummary
    
#     headers = {
#         'X-RapidAPI-Key': 'b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8',
#         'X-RapidAPI-Host': 'cricbuzz-cricket.p.rapidapi.com'
#     }
    
#     matches = Matches.objects.exclude(state = 'Upcoming').exclude(state = 'Complete')
    
#     for match in matches:
#         oversummary_url= f'https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match.match_id}/comm'
#         # store_oversummary(oversummary_url,headers)
    
#     try:
#         response= requests.get(oversummary_url, headers=headers)
#         response.raise_for_status()
        
#         if response.status_code == 200:
#             data = response.json()
#             match_id = data.get('matchHeader', {}).get('matchId')
#             commentary_list = data.get('commentaryList', [])
            
            
#             for commentary in commentary_list:
#                 OverSummary.objects.create(
#                 match_id = match_id,
#                 InningsId=str(commentary.get('inningsId', '')),
#                 OverNum=str(commentary.get('overNumber', '')),
#                 Event=commentary.get('event', ''),
#                 commentary=commentary.get('commText', '')
#                 )
                    
            
#     except requests.RequestException as e:
#         print(f'Failed to fetch oversummary from api: {oversummary_url}, Error: {e}')
        
#     return render(request, 'Home/home.html')

class MatchesList(APIView):
    def get(self, request):
        today=timezone.now()
        five_days_earlier = today - timedelta(days=7)
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
        


