from django.db import models


class Teams(models.Model):
    name = models.CharField(max_length=50, unique=True)


class News(models.Model):
    date = models.DateTimeField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    title = models.TextField()
    source = models.URLField(unique=True)

    def __str__(self):
        return f'<News: {self.title} from {self.source}>'


class StatEpl(models.Model):
    position = models.IntegerField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    matches = models.IntegerField()
    win = models.IntegerField()
    draw = models.IntegerField()
    loss = models.IntegerField()
    scored = models.IntegerField()
    conceded = models.IntegerField()
    points = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<News: {self.team.name} has {self.points}>. Season - {self.season}'


class GoalscorersEPL(models.Model):
    position = models.IntegerField()
    player = models.CharField(max_length=50)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    goals = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<News: {self.player} has {self.goals} goals>. Season - {self.season}'


class AssistentsEPL(models.Model):
    position = models.IntegerField()
    player = models.CharField(max_length=50)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    assists = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<News: {self.player} has {self.assists} assists>. Season - {self.season}'


class CalendarMatches(models.Model):
    date_match = models.DateTimeField()
    tournament = models.CharField(max_length=50)
    opposite_team = models.CharField(max_length=50)
    place_match = models.CharField(max_length=10)
    match_score = models.CharField(max_length=10)
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<News: Match against {self.opposite_team}. Score: {self.match_score}.'
