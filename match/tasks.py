from celery import shared_task
from rest_framework.response import Response
import requests
import datetime
from django.utils.timezone import make_aware
import math
from .comment_sentiment import predict_sentiment



# Storing MacthesList
def Store_And_Update_Matches(api_url, headers):
    from .models import Matches,Series
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            match_data = response.json()
            
            for match_type in match_data['typeMatches']:
                
                if match_type['matchType'] == 'Women':
                    continue

                for series_match in match_type['seriesMatches']:
                    matches = series_match.get('seriesAdWrapper', {}).get('matches', [])
                    series_info = series_match.get('seriesAdWrapper', {})
                    series_id = series_info.get('seriesId')
                    series_name = series_info.get('seriesName', 'Unknown Series')

                    # creating seires object
                    if matches:
                        first_match_info = matches[0]['matchInfo']
                        series_start_timestamp = first_match_info.get('seriesStartDt')
                        series_end_timestamp = first_match_info.get('seriesEndDt')
                    
                    
                    # Convert timestamps to datetime objects
                    series_start_date = None
                    series_end_date = None  
                    if series_start_timestamp:
                        series_start_date = make_aware(
                            datetime.datetime.fromtimestamp(int(series_start_timestamp) / 1000.0)
                        )
                    if series_end_timestamp:
                        series_end_date = make_aware(
                            datetime.datetime.fromtimestamp(int(series_end_timestamp) / 1000.0)
                        )
                        
                    # print(series_id,series_name,series_start_date,series_end_date) 
                    series_obj = None
                    if series_id:
                        series_obj, created = Series.objects.get_or_create(
                            series_id=series_id,
                            defaults={
                                'series_name': series_name,
                                'start_date': series_start_date,
                                'end_date': series_end_date,
                            }
                        )
                        
                        if created:
                            print(f"Created new Series")
                        else:
                            print(f"Series already exists")
                
                    
                    for match_info in matches:
                        
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
                                series = series_obj if series_obj else None,
                                match_type=match_type['matchType'],
                                series_name=series_name,
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
        
        
# Storing OverSummary
def store_oversummary(oversummary_url, headers):
    from .models import Matches,OverSummary,Scoreboard
    
    try:
        response= requests.get(oversummary_url, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            matchHeader = data.get('matchHeader', {})
            match_id = matchHeader.get('matchId')
            state = matchHeader.get('state')
            commentary_list = data.get('commentaryList', [])
            
            match = Matches.objects.filter(match_id=match_id).first()
            
            miniscore = data.get("miniscore", {})
            match_score_details = miniscore.get("matchScoreDetails", {})
            innings_score_list = match_score_details.get("inningsScoreList", [])
            
            match.innings_id =str(miniscore.get('inningsId') or '1')
            match.state = state
            match.save()
            
            
            # Update Scoreboard fields
            for innings in innings_score_list:
                inningsId = str(innings.get("inningsId") or '1')
                bat_team_name = innings.get('batTeamName')
                score = innings.get("score", 0)
                overs = innings.get("overs", 0)
                wickets = innings.get("wickets", 0)
                
                
                scoreboard, created = Scoreboard.objects.update_or_create(
                        match=match,
                        inningsId=inningsId,
                        defaults={
                            'bat_team': bat_team_name,
                            'score': score,
                            'wickets': wickets,
                            'overs': overs,
                        }
                    )
                    
                    
    
            previous = 0.0
            for commentary in commentary_list:
                innings_id = str(commentary.get('inningsId') or '1')
                over_num = commentary.get('overNumber') or previous
                event = commentary.get('event', '')
                comm_text = commentary.get('commText', '')
                previous = over_num+0.01
                
                if abs(over_num % 1 - 0.6) < 0.001:
                    over_num = math.ceil(over_num)

                OverSummary.objects.get_or_create(
                    match_id=match_id,
                    InningsId=innings_id,
                    OverNum=over_num,
                    commentary=comm_text,
                    defaults={
                        'Event': event,
                    }
                )
                    
            
    except requests.RequestException as e:
        print(f'Failed to fetch oversummary from api: {oversummary_url}, Error: {e}')
    
    
    
    
    
    

@shared_task(bind=True)
def fetch_matches_from_api(self):
    # Niloy Das
    # headers = {
    #     "x-rapidapi-key": "2c9bb38fd1msh7f2cfcda4cf807ep11c91ajsn7e28e3ba076e",
    #     "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    # }
    
    # Nitay
    headers = {
        'X-RapidAPI-Key': 'b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8',
        'X-RapidAPI-Host': 'cricbuzz-cricket.p.rapidapi.com'
    }
    
    # srijon
    # headers = {
    # 'x-rapidapi-key': "b26e37462cmshe185bdd3da287b2p1d13c7jsn4894941c8da9",
    # 'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    # }
    

    
    
    upcoming_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming'
    Store_And_Update_Matches(upcoming_api_url, headers)
    
    live_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live'
    Store_And_Update_Matches(live_api_url, headers)
    
    recent_api_url = 'https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent'
    Store_And_Update_Matches(recent_api_url, headers)
    
    return "Done"


@shared_task(bind=True)
def fetch_oversummary(self):
    from .models import Matches
    
   
    #srijon
    headers = {
    'x-rapidapi-key': "b26e37462cmshe185bdd3da287b2p1d13c7jsn4894941c8da9",
    'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }
    
    matches = Matches.objects.exclude(state = 'Upcoming').exclude(state = 'Complete').exclude(match_type = 'League').exclude(match_type = 'Domestic')
    
    for match in matches:
        oversummary_url= f'https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match.match_id}/comm'
        store_oversummary(oversummary_url,headers)
    
    return "Done"



@shared_task
def check_sentiment_and_censor(comment_id):
    from .models import Comment
    try:
        comment = Comment.objects.get(id=comment_id)
        sentiment = predict_sentiment(comment.content)
        print("sentiment", sentiment)

        # If sentiment is very negative, censor it
        if sentiment[0].strip() == 'Very Negative':  # Adjust condition as needed
            print("yes")
            comment.content = "****"
            comment.save()
    except Comment.DoesNotExist:
        pass

    
    
     
     