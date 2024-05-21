from celery import shared_task
from rest_framework.response import Response
import requests
import datetime
from django.utils.timezone import make_aware

def Store_And_Update_Matches(api_url, headers):
    from .models import Matches
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            match_data = response.json()
            
            for match_type in match_data['typeMatches']:
                
                if match_type['matchType'] == 'Women':
                    continue

                for series_match in match_type['seriesMatches']:
                    for match_info in series_match.get('seriesAdWrapper', {}).get('matches', []):
                        
                        match_id = match_info['matchInfo']['matchId']
                        existing_match = Matches.objects.filter(match_id=match_id).first()
                        
                        start_timestamp = match_info['matchInfo'].get('startDate')
                        start_date = None
                        if start_timestamp:
                            try:
                                start_date = make_aware(datetime.datetime.fromtimestamp(int(start_timestamp) / 1000.0))
                            except ValueError:
                                print(f"Invalid timestamp: {start_timestamp}")
                                    
                        if not existing_match:
                            
                            Matches.objects.create(
                                match_id=match_info['matchInfo']['matchId'],
                                series_id=match_info['matchInfo']['seriesId'],
                                match_type=match_type['matchType'],
                                series_name=match_info['matchInfo']['seriesName'],
                                team1=match_info['matchInfo']['team1']['teamName'],
                                team2=match_info['matchInfo']['team2']['teamName'],
                                match_description=match_info['matchInfo']['matchDesc'],
                                status=match_info['matchInfo'].get('status', None),
                                venue=match_info['matchInfo']['venueInfo']['ground'],
                                state=match_info['matchInfo']['state'],
                                start_date=start_date
                            )
                            
                        else:
                            existing_match.status = match_info['matchInfo'].get('status', None)
                            existing_match.state = match_info['matchInfo']['state']
                            existing_match.start_date = start_date 
                            existing_match.save()
        else:
            print(f'Failed to fetch matches from API: {api_url}')

    except requests.RequestException as e:
        print(f'Failed to fetch matches from API: {api_url}, Error: {e}')



@shared_task(bind=True)
def fetch_matches_from_api(self):
    
    headers = {
        'X-RapidAPI-Key': 'b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8',
        'X-RapidAPI-Host': 'cricbuzz-cricket.p.rapidapi.com'
    }
    
    upcoming_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming'
    Store_And_Update_Matches(upcoming_api_url, headers)
    
    live_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live'
    Store_And_Update_Matches(live_api_url, headers)
    
    # recent_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent'
    # Store_And_Update_Matches(recent_api_url, headers)
    
    return "Done"