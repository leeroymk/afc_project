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
