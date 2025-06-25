from rest_framework import serializers
from .models import Song  
from .models import SearchSong

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song  
        fields = '__all__' 

    def validate(self, data):
        """
        Custom validation logic can be added here if needed.
        """
        return data

class SearchSongsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSong  
        fields = '__all__' 

    def validate(self, data):
        """
        Custom validation logic can be added here if needed.
        """
        return data