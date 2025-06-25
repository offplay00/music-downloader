from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import Song, SearchSong
from .serializers import SongSerializer, SearchSongsSerializer
from .business_logic import delete_song, handle_song_search
import logging

logger = logging.getLogger('core')


class SongViewSet(ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    @action(detail=False, methods=['get'], url_path='songs')
    def list_songs(self, request):
        """Lists all songs."""
        serializer = SongSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieves a specific song by ID."""
        song = get_object_or_404(Song, pk=pk)
        serializer = SongSerializer(song)
        return Response(serializer.data)

    def create(self, request):
        """Creates a new song."""
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Deletes a song."""
        song = get_object_or_404(Song, pk=pk)
        response = delete_song(song.id)
        if response == 1:
            return Response({"message": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
        elif response == 2:
            return Response({"message": "Error while deleting song"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif response == 0:
            song.delete()
            return Response({"message": "Song deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Unknown error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchSongs(ModelViewSet):
    queryset = SearchSong.objects.all()
    serializer_class = SearchSongsSerializer

    def create(self, request, *args, **kwargs):
        """Creates a new search song entry and triggers the search."""
        data, status_code = handle_song_search(request.data)
        return Response(data, status=status_code)
