from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404 
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Song, SearchSong
from .serializers import SongSerializer, SearchSongsSerializer
from .business_logic import search_song_by_title as search_song_by_title, download_song_details as download_song_details, delete_song as delete_song
import logging

logger = logging.getLogger('core') 

class SongViewSet(ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    @action(detail=False, methods=['get'], url_path='songs') 
    def list_songs(self, request):
        serializer = SongSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        song = get_object_or_404(Song, id=kwargs.get('pk'))
        serializer = SongSerializer(song)
        return Response(serializer.data)

    def post(self, request):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, *args, **kwargs):
        song = get_object_or_404(Song, id=kwargs.get('pk'))
        response = delete_song(song.id)
        if response == 1:
            return Response({"message": "Song not found"}, status=404)
        elif response == 2:
            return Response({"message": "Error while deleting song"}, status=500)
        elif response == 0:
            song.delete()
            return Response({"message": "Song deleted successfully"}, status=200)


class SearchSongs(ModelViewSet):
    queryset = SearchSong.objects.all()

    def create(self, request, *args, **kwargs):
        data, status_code = handle_song_search(request.data)
        return Response(data, status=status_code)
        