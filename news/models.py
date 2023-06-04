from django.db import models


class News(models.Model):
    # TODO: change date type from str to datetime
    # TODO: fix max lengths
    news_date = models.CharField(max_length=10)
    news_title = models.CharField(max_length=100)
    news_context = models.CharField(max_length=200)
    news_source = models.CharField(max_length=30)

    def __str__(self):
        return f'<News: {self.news_title} from {self.news_source}>'
