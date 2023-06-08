from django.db import models


class News(models.Model):
    # TODO: change date type from str to datetime
    # TODO: fix max lengths
    news_date = models.CharField(max_length=50)
    news_title = models.CharField(max_length=200)
    news_context = models.TextField()
    news_source = models.CharField(max_length=200)

    def __str__(self):
        return f'<News: {self.news_title} from {self.news_source}>'
