from django.db import models

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
    status = models.CharField(max_length=100)
    venue = models.CharField( max_length=100)
    state = models.CharField(max_length=50)
   

    def __str__(self):
        return f"{self.match_description} ({self.match_id})"