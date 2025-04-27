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
import re
from langdetect import detect
from .tasks import check_sentiment_and_censor
from .comment_sentiment import predict_sentiment
from report.views import update_comment_stats_for_comment, update_match_comment_stats

slang_words_map = {
    "en": [
        "badword", "swearword", "insult", "curseword"  # Add English slang words
    ],
    "bn": [
        "অশ্লীল", "অপমানজনক", "অভদ্র", "অশোভন", "গালি"  # Add Bengali slang words
    ],
    "es": [
        "maldición", "grosería", "insulto"  # Add Spanish slang words
    ],
    "fr": [
        "injure", "grossièreté", "insulte"  # Add French slang words
    ]
}



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
        five_days_earlier = today - timedelta(days=50)
        seven_days_later = today + timedelta(days=50)
        matches=Matches.objects.filter(start_date__date__range=(five_days_earlier.date(),seven_days_later.date()))
        serializer = MatchesSerializer(matches,many=True)
        return Response(serializer.data)
    

    
class overSummary_and_Scoreboard(APIView):
    permission_classes = [AllowAny]
    def get(self, request, match_id):
        
        try:
             match = Matches.objects.get(match_id=match_id)
             innings_id = request.data.get('innings_id') 
             
        except Matches.DoesNotExist:
            return Response({"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch and serialize scoreboard data
        scoreboard = Scoreboard.objects.filter(match=match)
        scoreboard_serializer = ScoreboardSerializer(scoreboard, many=True)
        
        # Fetch and serialize over summary data
        innings_id = innings_id if innings_id else match.innings_id
        oversummary = OverSummary.objects.filter(match_id=match_id, InningsId = innings_id)
        oversummary_serializer = OverSummarySerializer(oversummary, many=True)
        
        # Combine all serialized data into one response
        response_data = {
            "scoreboard": scoreboard_serializer.data,
            "oversummary": oversummary_serializer.data,
            "match_info": f"{match.status} --- {match.series_name}",
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    

# return ball by ball striker batsman and bowler info 
class BallByBallView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, match_id):
        
        try:
            match = Matches.objects.get(match_id=match_id)
            
        except Matches.DoesNotExist:
            return Response({"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND)
        
         # Fetch and serialize scoreboard data
        striker_info = StrikerInfo.objects.filter(match=match)
        StrikerInfoserializer = StrikerInfoSerializer(striker_info, many=True)
        
        return Response(StrikerInfoserializer.data, status=status.HTTP_200_OK)
    
    

def filter_slang_words(content):
    try:
        # Detect the language of the content
        detected_language = detect(content)
    except Exception:
        # Default to English if detection fails
        detected_language = "en"
        
    # print(detected_language)
    
    # Get the slang words for the detected language, default to English if not found
    slang_words = slang_words_map.get(detected_language, slang_words_map.get("en", []))
    # print(slang_words)
    
    # Tokenize the input text
    words = re.findall(r'\b\w+\b|[^\w\s]', content, re.UNICODE)
    # print(words)
    
    # Create a set of slang words for faster lookup
    slang_set = set(slang_words)
    
    pattern = r'\b(' + '|'.join(map(re.escape, slang_words)) + r')\b'
    return re.sub(pattern, '***', content, flags=re.IGNORECASE | re.UNICODE)
    
    # # Replace any slang word with '***'
    # filtered_words = [
    #     '***' if word in slang_set else word
    #     for word in words
    # ]
    
    # Reconstruct the content
    return ''.join(
        filtered_words[i] + ' ' if filtered_words[i].isalnum() else filtered_words[i]
        for i in range(len(filtered_words))
    )



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
       comment = request.data.get("content", "")
       
      
       slang_words = ["shala", "bloody", "stupid", "শালা"]
       # Filter slang words from the comment content
       filtered_content = filter_slang_words(comment)
       
       data = {
            "event": event.id,  
            "user": request.data.get("user"),
            "content": filtered_content,
            "parent": parent_id if parent_id else None,
            
        }


       serializer = CommentSerializer(data=data)
       if serializer.is_valid():
            comment_instance = serializer.save()
            
            
            #trigger the predict function
            check_sentiment_and_censor.delay(comment_instance.id)
    
            update_match_comment_stats()
            update_comment_stats_for_comment(comment_instance)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
       print(serializer.errors)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   

class LikeCommentView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request, comment_id):
        user_email = request.data.get('user_email') 
        
        if not user_email:
            return Response({'error': 'User email not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Comment.objects.get(id=comment_id)
            comment.toggle_like(user_email)  
            return Response({
                'likes': comment.likes,
                'liked_by': comment.liked_by,
                'comment': CommentSerializer(comment).data  
            }, status=status.HTTP_200_OK)
            
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class GetTopComments(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        today = timezone.now()
        Ten_days_earlier = today - timedelta(days=9)
        comments = Comment.objects.filter(created_at__gte=Ten_days_earlier.date()).order_by('-likes', '-created_at')[:20]

        serializer = topCommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetRecentComments(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        today = timezone.now()
        Ten_days_earlier = today - timedelta(days=9)
        comments = Comment.objects.filter(created_at__gte=Ten_days_earlier.date()).order_by('-created_at')[:25]

        serializer = topCommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class GetNews(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        today = timezone.now()
        Five_days_earlier = today - timedelta(days=5)
        news = Story.objects.filter(pub_time__gte=Five_days_earlier.date()).order_by('pub_time')
        serializer = NewsSerializer(news, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

