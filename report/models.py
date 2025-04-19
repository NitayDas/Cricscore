from django.db import models

class MatchCommentStats(models.Model): 
    MATCH_TYPE_CHOICES = [ ('International', 'International'), ('League', 'League'), ('Domestic', 'Domestic'), ]

    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, unique=True)
    t20_count = models.PositiveIntegerField(default=0)
    one_day_count = models.PositiveIntegerField(default=0)
    test_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.match_type} | T20: {self.t20_count}, ODI: {self.one_day_count}, Test: {self.test_count}"
