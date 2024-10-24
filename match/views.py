from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,generics
from .serializers import *
from .models import *
from django.utils import timezone
from datetime import datetime,timedelta
import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


def home(request):
    return render(request, 'Home/home.html')

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        print(username)
        
       
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log in the user (session-based authentication)
            return Response({'message': 'Login successful!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
class SeriesList(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        today=timezone.now()
        thirty_days_earlier = today - timedelta(days=30)
        Thirty_days_later = today + timedelta(days=30)
        series=Series.objects.filter(start_date__date__range=(thirty_days_earlier.date(),Thirty_days_later.date())).order_by('-start_date') 
        serializer = SeriesSerializer(series,many=True)
        return Response(serializer.data)
    
    
class SeriesMatchesList(APIView):
    permission_classes = [AllowAny]
    def get(self, request, seriesId):
        series = Series.objects.get(series_id = seriesId)
        matches = Matches.objects.filter(series=series).order_by('-start_date') 
        serializer = SeriesMatchesSerializer(matches,many=True)
        return Response(serializer.data)
        
    
class MatchesList(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        today=timezone.now()
        five_days_earlier = today - timedelta(days=10)
        seven_days_later = today + timedelta(days=10)
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
    permission_classes = [AllowAny]
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
            "oversummary": oversummary_serializer.data,
            "match_info": f"{match.status} --- {match.series_name}",
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        


class CommentView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, over_summary_id):
        try:
            over_summary = OverSummary.objects.get(id=over_summary_id)
            comments = over_summary.comments.filter(parent__isnull=True).prefetch_related('replies')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        
        except OverSummary.DoesNotExist:
            return Response({'error': 'OverSummary not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, over_summary_id):
       try:
            event = OverSummary.objects.get(id=over_summary_id)
            
       except OverSummary.DoesNotExist:
            return Response({'error': 'OverSummary not found.'}, status=status.HTTP_404_NOT_FOUND)

       parent_id = request.data.get("parent")
       
       
       data = {
            "event": event.id,  
            "user": request.data.get("user"),
            "content": request.data.get("content"),
            "parent": parent_id if parent_id else None,
            
        }

       serializer = CommentSerializer(data=data)
       if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
       print(serializer.errors)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   

# class ReplyListCreateView(generics.ListCreateAPIView):
    # pass
#     serializer_class = ReplySerializer

#     def get_queryset(self):
#         comment_id = self.kwargs['comment_id']
#         return Comment.objects.filter(parent_id=comment_id).order_by('-created_at')

#     def perform_create(self, serializer):
#         comment_id = self.kwargs['comment_id']
#         parent_comment = Comment.objects.get(id=comment_id)
        
#         reply_content = serializer.validated_data.get('content')  # Reply content
#         username = serializer.validated_data.get('username')      # Username

#         # Print the reply content and username
#         print(f"Reply Content: {reply_content}")
#         print(f"Username: {username}")
#         serializer.save(parent=parent_comment, event=parent_comment.event)   
        
        
   
@api_view(['GET']) 
def get_current_user(request):
    user= request.user
    print(user.username)
    if user.is_authenticated:
         return JsonResponse({'username': user.username})
    else:
         return JsonResponse({'error': 'User not authenticated'}, status=401)