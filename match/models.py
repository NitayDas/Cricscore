from django.db import models
from django.utils.translation import gettext_lazy as _

class Matches(models.Model):
    match_id = models.CharField(null=True,max_length=100)
    series_id = models.CharField(null=True,max_length=100)
    match_type = models.CharField(max_length=50)
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
    OverNum = models.CharField(null=True,max_length=100)
    Event = models.CharField(null=True,max_length=100)
    commentary = models.CharField(null=True,max_length=3000)
    
    
    def __str__(self):
        return f"{self.match_id}-{self.InningsId}-({self.OverNum})"
    
    
    