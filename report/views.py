from django.shortcuts import render
from match.models import Comment, Matches, OverSummary
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import MatchCommentStats, TeamCommentStats
from .serializers import MatchCommentStatsSerializer, TeamCommentStatsSerializer


    
        
class CommentSentimentReportView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        comments = Comment.objects.all()  
        total_comments = comments.count()  
        bad_comments = 0  

        for comment in comments:  
            if '****' in comment.content:  
                bad_comments += 1  

        good_comments = total_comments - bad_comments  

        # Calculate percentages  
        good_percent = (good_comments / total_comments) * 100 if total_comments > 0 else 0  
        bad_percent = (bad_comments / total_comments) * 100 if total_comments > 0 else 0  

        report = {  
            'total_comments': total_comments,  
            'good_comments': good_comments,  
            'bad_comments': bad_comments,  
            'good_percentage': round(good_percent, 2),  
            'bad_percentage': round(bad_percent, 2),  
        }  

        return Response(report, status=status.HTTP_200_OK)
    
    
class CommentMatchTypeReportView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request): 
        stats = MatchCommentStats.objects.all() 
        serializer = MatchCommentStatsSerializer(stats, many=True) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class TeamCommentStatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        stats = TeamCommentStats.objects.all()
        serializer = TeamCommentStatsSerializer(stats, many=True)
        return Response(serializer.data)
    


def update_match_comment_stats(): 
    formats = ['T20', 'One Day', 'TEST'] 
    types = ['International', 'League', 'Domestic']

    for match_type in types:
        # Initialize counters
        counts = {
            'T20': 0,
            'One Day': 0,
            'TEST': 0,
        }

        # Get matches of this type
        matches = Matches.objects.filter(match_type=match_type)

        # Map match_id to match_format
        match_format_map = {m.match_id: m.match_format for m in matches}

        # Get OverSummaries for these matches
        summaries = OverSummary.objects.filter(match_id__in=match_format_map.keys())

        for summary in summaries:
            match_format = match_format_map.get(summary.match_id)
            if match_format in formats:
                counts[match_format] += summary.comments.count()

        # Save or update
        MatchCommentStats.objects.update_or_create(
            match_type=match_type,
            defaults={
                't20_count': counts['T20'],
                'one_day_count': counts['One Day'],
                'test_count': counts['TEST'],
            }
        )
        
        
    


def update_comment_stats_for_comment(comment):
    try:
        event = comment.event
        match_id = event.match_id

        match = Matches.objects.filter(match_id=match_id).first()
        if not match:
            return  # No match found

        stats_obj, created = MatchCommentStats.objects.get_or_create(match_type=match.match_type)

        # Step 5: Normalize match format
        match_format = (match.match_format or '')
        format_map = {
            'T20': 't20_count',
            'Oneday': 'one_day_count',
            'Test': 'test_count',
        }
        field_name = format_map.get(match_format)
        if not field_name:
            return  # Unknown format, skip

        # Step 6: Increment the count
        current_value = getattr(stats_obj, field_name, 0)
        setattr(stats_obj, field_name, current_value + 1)
        stats_obj.save()

    except Exception as e:
        print("Error updating CommentStats:", str(e))
        
        
        

def update_team_comment_stats(comment,sentiment):
    try:
        over_summary = comment.event
        match = Matches.objects.get(match_id=over_summary.match_id)
        
        print("ReportSentiment:", sentiment)
        
        # Update stats for both teams
        for team in [match.team1, match.team2]:
            stats, created = TeamCommentStats.objects.get_or_create(team_name=team)
            if sentiment[0].strip() == 'Very Negative':
                stats.bad_comments += 1
            else:
                stats.good_comments += 1
            stats.save()
    except Matches.DoesNotExist:
        print("Match not found for the comment")
    except Exception as e:
        print(f"Error updating team comment stats: {str(e)}")
