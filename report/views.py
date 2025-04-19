from django.shortcuts import render
from match.models import Comment, Matches
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import MatchCommentStats


class CommentMatchTypeReportView(APIView): 
    permission_classes = [AllowAny]
    def get(self, request):  
        comments = Comment.objects.select_related('event')  

        level_count = {  
            'International': 0,  
            'Domestic': 0,  
            'League': 0,  
            'Unknown': 0  
        }  

        total_comments = 0  

        for comment in comments:  
            over_summary = comment.event  
            match = Matches.objects.filter(match_id=over_summary.match_id).first()  

            if match:  
                level = getattr(match, 'match_type', '').lower()  

                if 'international' in level:  
                    level_count['International'] += 1  
                elif 'domestic' in level:  
                    level_count['Domestic'] += 1  
                elif 'league' in level:  
                    level_count['League'] += 1  
                else:  
                    level_count['Unknown'] += 1  

                total_comments += 1  

        # Calculate percentage  
        report = {}  
        for key in level_count:  
            percentage = (level_count[key] / total_comments) * 100 if total_comments > 0 else 0  
            report[key] = {  
                'count': level_count[key],  
                'percentage': round(percentage, 2)  
            }  

        return Response({  
            'total_comments': total_comments,  
            'match_level_distribution': report  
        }, status=status.HTTP_200_OK)
            
    
    
        
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
