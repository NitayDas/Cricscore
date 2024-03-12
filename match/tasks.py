from celery import shared_task
from rest_framework.response import Response
import requests

   
@shared_task(bind=True)
def fetch_matches_from_api(self):
    from .models import Matches
    
    print("1000")
    
    live_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live'
    upcoming_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming'
    
    headers = {
        'X-RapidAPI-Key': 'b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8',
        
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }
    
    try:
        
        upcoming_response = requests.get(upcoming_api_url, headers=headers)
        upcoming_response.raise_for_status() 
        
        if upcoming_response.status_code == 200:
            upcoming_match = upcoming_response.json()
            # print(upcoming_match)
            
            for match_type in upcoming_match['typeMatches']:
                
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
            print('Failed to fetch upcoming_matches from API')
                
    except requests.RequestException as e:
        return Response({'error': f'Failed to fetch upcoming_matches from API: {e}'}, status=500)
    
    
    
    try:
        
        live_response = requests.get(live_api_url, headers=headers)
        live_response.raise_for_status() 
        
        if live_response.status_code == 200:
            live_match = live_response.json()
            
            for match_type in live_match['typeMatches']:
                
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
            print('Failed to fetch live_matches from API')
                
    except requests.RequestException as e:
        return Response({'error': f'Failed to fetch live_matches from API: {e}'}, status=500)
        
        