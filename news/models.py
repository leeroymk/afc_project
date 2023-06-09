from django.db import models


class News(models.Model):
    # TODO: change date type from str to datetime
    date = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    source = models.URLField(max_length=200)

    def __str__(self):
        return f'<News: {self.title} from {self.source}>'
