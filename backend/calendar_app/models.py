from django.db import models


class WatchlistCache(models.Model):
    username = models.CharField(max_length=255, unique=True)
    fetched_at = models.DateTimeField(auto_now=True)
    items = models.JSONField(default=list)
    count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.username


class TMDBMovieCache(models.Model):
    tmdb_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=512)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    overview = models.TextField(blank=True)
    release_dates = models.JSONField(default=dict)
    fetched_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.tmdb_id})"
