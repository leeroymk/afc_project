from django.db import models


class Teams(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(null=True)
    slug = models.CharField(max_length=25, null=True)
    logo = models.URLField(null=True)
    league = models.CharField(max_length=50)

    def __str__(self):
        return f'<Teams: name: {self.name}, URL:{self.url}>'


class News(models.Model):
    date = models.DateTimeField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    title = models.TextField()
    source = models.URLField(unique=True)

    def __str__(self):
        return f'<News: team: {self.team}, title: {self.title}, source: {self.source}, date: {self.date}>'


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
        return f'<Stat: team: {self.team.name}, points: {self.points}>. Season: {self.season}'


class GoalscorersEPL(models.Model):
    position = models.IntegerField()
    player = models.CharField(max_length=50)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    goals = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<Goals: player: {self.player}, goals: {self.goals}>. Season: {self.season}'


class AssistantsEPL(models.Model):
    position = models.IntegerField()
    player = models.CharField(max_length=50)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    assists = models.IntegerField()
    season = models.CharField(max_length=15)

    def __str__(self):
        return f'<Assistants: player: {self.player}, assists: {self.assists}>. Season: {self.season}'


class CalendarMatches(models.Model):
    date_match = models.DateTimeField()
    tournament = models.CharField(max_length=50)
    place_match = models.CharField(max_length=10)
    match_score = models.CharField(max_length=10)
    season = models.CharField(max_length=15)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    rival = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='rival')

    def __str__(self):
        return f'<Calendar: team: {self.team.name} rival: {self.rival.name}, score: {self.match_score}, date: {self.date_match}>. Season {self.season}'
