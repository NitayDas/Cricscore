# tasks.py
from celery import shared_task
from celery.schedules import crontab
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *

    
@shared_task(bind=True)
def fetch_matches_from_api(self):
    
    print("1000")
    
    api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming'
    headers = {
        'X-RapidAPI-Key': 'b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8',
        
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        matches_data = response.json()
        # print(matches_data)
        
        for match_type in matches_data['typeMatches']:
            
            for series_match in match_type['seriesMatches']:
                
                 for match_info in series_match.get('seriesAdWrapper', {}).get('matches', []):
                     
                     match_id = match_info['matchInfo']['matchId']
                     existing_match = Matches.objects.filter(match_id=match_id).first()
                     if not existing_match:
                         
                         Matches.objects.create(
                                match_id=match_info['matchInfo']['matchId'],
                                series_id=match_info['matchInfo']['seriesId'],
                                match_type=match_type['matchType'],
                                series_name=match_info['matchInfo']['seriesName'],
                                team1=match_info['matchInfo']['team1']['teamName'],
                                team2=match_info['matchInfo']['team2']['teamName'],
                                match_description=match_info['matchInfo']['matchDesc'],
                                status=match_info['matchInfo']['status'],
                                venue=match_info['matchInfo']['venueInfo']['ground'],
                                state=match_info['matchInfo']['state']
                            )
    else:
        print('Failed to fetch matches from API')
        
    return "done"
        


