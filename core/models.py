from django.db import models

# Create your models here.
class Song(models.Model):
    id = models.TextField(primary_key=True)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100, null=True, blank=True)
    album = models.CharField(max_length=100, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=50, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    url = models.TextField()
    cover_image = models.TextField(null=True, blank=True)
    lyrics = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.artist or 'Unknown Artist'} from {self.album or 'Unknown Album'}"

class SearchSong(models.Model):
    query = models.CharField(max_length=200)

    def __str__(self):
        return f"Search for: {self.query}"