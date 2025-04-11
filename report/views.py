from django.shortcuts import render
from match.models import Comment, Matches
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


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
