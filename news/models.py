from django.db import models


class News(models.Model):
    # TODO: change date type from str to datetime
    date = models.DateTimeField()
    team = models.CharField(max_length=50)
    title = models.TextField()
    source = models.URLField()

    def __str__(self):
        return f'<News: {self.title} from {self.source}>'


class StatEpl(models.Model):

    position = models.IntegerField()
    team = models.CharField(max_length=50)
    matches = models.IntegerField()
    win = models.IntegerField()
    draw = models.IntegerField()
    loss = models.IntegerField()
    scored = models.IntegerField()
    conceded = models.IntegerField()
    points = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<News: {self.team_name} has {self.points}>. Season - {self.season}'
