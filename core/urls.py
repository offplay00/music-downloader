from django.urls import path
from .views import SongViewSet, SearchSongs
 
urlpatterns = [
    path('songs/', SongViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('songs/<str:pk>', SongViewSet.as_view({'get': 'retrieve'})),
    path('songs/delete/<str:pk>', SongViewSet.as_view({'delete': 'delete'})),
    path('search/',SearchSongs.as_view({'post': 'create'}))   
]
