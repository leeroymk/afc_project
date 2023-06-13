from django.db import models


class News(models.Model):
    # TODO: change date type from str to datetime
    date = models.DateTimeField()
    team = models.CharField(max_length=50)
    title = models.TextField()
    source = models.URLField()

    def __str__(self):
        return f'<News: {self.title} from {self.source}>'
