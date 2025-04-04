import requests
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
import datetime


@shared_task
def fetch_and_store_stories():
    from .models import Story, CoverImage
    api_url= "https://cricbuzz-cricket.p.rapidapi.com/news/v1/index"
    
    # Niloy Das
    headers = {
        "x-rapidapi-key": "2c9bb38fd1msh7f2cfcda4cf807ep11c91ajsn7e28e3ba076e",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    
    try:
        
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            story_list = response.json().get('storyList', [])

            for item in story_list:
                story_data = item.get('story', {})
                print(story_data)
                
                story_id = story_data.get('id') 
                
                if not story_id: 
                    print("Story ID is missing. Skipping this entry.")
                    continue

                cover_image_data = story_data.get('coverImage', {})
                cover_image_id = cover_image_data.get('id')
                if cover_image_id:
                    cover_image, _ = CoverImage.objects.get_or_create(
                        id=cover_image_id,
                        defaults={'caption': cover_image_data.get('caption')}
                    )

                pub_time_timestamp = story_data.get('pubTime')
                pub_time = None
                if pub_time_timestamp:
                    pub_time = make_aware(
                        datetime.datetime.fromtimestamp(int(pub_time_timestamp) / 1000.0)
                    )
                
                # Create or get the story
                Story.objects.get_or_create(
                    story_id=story_id,
                    defaults={
                        'headline': story_data.get('hline', ''),
                        'intro': story_data.get('intro', ''),
                        'pub_time': pub_time,
                        'source': story_data.get('source', ''),
                        'story_type': story_data.get('storyType', ''),
                        'image_id': story_data.get('imageId'),
                        'context': story_data.get('context', ''),
                        # Add more fields if required
                    }
                )
        else:
            print(f"Failed to fetch stories: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to fetch stories: {api_url}, Error: {e}")
        
        
def store_ballByball(api_url, headers, querystring,match_id):
    from . models import Matches, BallByBall
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        try:
            # print(data)
            match = Matches.objects.get(match_id=match_id)
            
            miniscore = data.get("miniscore", {})

            batsman_striker = miniscore.get("batsmanStriker", {})
            batsman_non_striker = miniscore.get("batsmanNonStriker", {})
            bowler_striker = miniscore.get("bowlerStriker", {})
            bowler_non_striker = miniscore.get("bowlerNonStriker", {})
            cur_overs_stats = miniscore.get("curOvsStats", {})

            # Update or create BallByBall data
            BallByBall.objects.update_or_create(
                match=match,
                defaults={
                    "batsman_striker": batsman_striker,
                    "batsman_non_striker": batsman_non_striker,
                    "bowler_striker": bowler_striker,
                    "bowler_non_striker": bowler_non_striker,
                    "cur_overs_stats": cur_overs_stats,
                },
            )
            print(f"Ball-by-Ball data updated for Match {match_id}")
        
        except Matches.DoesNotExist:
            print(f"Match with ID {match_id} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    else:
        print(f"Failed to fetch data: {response.status_code}")

         
      
@shared_task
def fetch_ballByball():
    from .models import Matches
    matches = Matches.objects.exclude(state = 'Upcoming').exclude(state = 'Complete').exclude(match_type = 'League').exclude(match_type = 'Domestic')
    
    # nitay
    # headers = {
    #     "x-rapidapi-key": "b75aac835cmshaa98b93c54be468p128cc8jsn66c9ac71b9e8",
    #     "x-rapidapi-host": "crickbuzz-official-apis.p.rapidapi.com"
    # }
    
     # Niloy Das
    headers = {
        "x-rapidapi-key": "2c9bb38fd1msh7f2cfcda4cf807ep11c91ajsn7e28e3ba076e",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    
    querystring = {"inning":"2","lastTimeStamp":"1664380633235"}
    
    for match in matches:
        url = f'https://crickbuzz-official-apis.p.rapidapi.com/match/{match.match_id}/overs'
        store_ballByball(url, headers, querystring, match.match_id)
      

    
