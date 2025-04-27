from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField


class Series(models.Model):
    series_id = models.CharField(max_length=100, unique=True)
    series_name = models.CharField(max_length=255)
    start_date = models.DateTimeField(null=True, blank=True)  
    end_date = models.DateTimeField(null=True, blank=True) 
   
    def __str__(self):
        return self.series_name

class Matches(models.Model):
    series = models.ForeignKey(Series, related_name='match', on_delete=models.CASCADE, null=True, blank=True)
    match_id = models.CharField(null=True,max_length=100)
    match_type = models.CharField(max_length=50)
    match_format = models.CharField(max_length=100, null=True, blank=True) 
    series_name= models.CharField(max_length=255)
    team1 = models.CharField(max_length=50)
    team2 = models.CharField(max_length=50)
    flag1 = models.ImageField(upload_to='images/', null=True, default=None)
    flag2 = models.ImageField(upload_to='images/', null=True, default=None)
    match_description = models.CharField(max_length=255)
    status = models.CharField(null=True,max_length=100)
    venue = models.CharField( max_length=100)
    state = models.CharField(max_length=50)
    start_date = models.DateTimeField(_("Start Date"), null=True, blank=True)
    innings_id = models.CharField(max_length=10,null=True,default=1)
   

    def __str__(self):
        return f"{self.match_description} ({self.match_id})"

class Scoreboard(models.Model):
    match = models.ForeignKey(Matches, on_delete=models.CASCADE)
    inningsId = models.CharField(max_length=10,default=1)
    bat_team = models.CharField(max_length=200,null = True)
    score = models.IntegerField(default=0)
    overs = models.FloatField(default=0.0)
    wickets = models.IntegerField(default=0)

    def __str__(self):
        return f"Scoreboard for Match: {self.match.id}-{self.inningsId}"
    
    
class OverSummary(models.Model):
    match_id = models.CharField(null=True,max_length=100)
    InningsId = models.CharField(max_length=100,default=1)
    OverNum = models.FloatField(null=True,max_length=100)
    Event = models.CharField(null=True,max_length=100)
    commentary = models.CharField(null=True,max_length=10000)
    
    
    def __str__(self):
        return f"{self.match_id}-{self.InningsId}-({self.OverNum})"
    
    
class StrikerInfo(models.Model):
    match = models.OneToOneField(Matches, on_delete=models.CASCADE, related_name="current_ball_by_ball")
    batsman_striker = models.JSONField() 
    batsman_non_striker = models.JSONField()  
    bowler_striker = models.JSONField() 
    bowler_non_striker = models.JSONField()  
    cur_overs_stats = models.TextField() 
    
    def __str__(self):
        return f"Current Ball-by-Ball for Match: {self.match.id}"
    
    
class Comment(models.Model):
    event = models.ForeignKey(OverSummary, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)  # For replies
    user = models.JSONField(null=True) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_by = models.JSONField(default=list)

    def __str__(self):
        return f'Comment by {self.user} on {self.event}'
    
    def toggle_like(self, user_email):
        if user_email in self.liked_by:
            self.liked_by.remove(user_email)
            self.likes -= 1
        else:
            self.liked_by.append(user_email)
            self.likes += 1
        self.save()
        
  
class CoverImage(models.Model):
    id = models.IntegerField(primary_key=True)
    caption = models.TextField()
    
    def __str__(self):
        return self.caption
    
             
class Story(models.Model):
    story_id = models.IntegerField(primary_key=True) 
    headline = models.CharField(max_length=255) 
    intro = models.TextField() 
    pub_time = models.DateTimeField() 
    source = models.CharField(max_length=100)
    story_type = models.CharField(max_length=50)
    image_id = models.IntegerField()
    context = models.CharField(max_length=50) 
    # cover_image = models.ForeignKey(CoverImage, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.headline


    
    
    
    