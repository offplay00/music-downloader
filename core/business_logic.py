import subprocess
import json
import os
import logging
from core.models import Song
from mutagen.easyid3 import EasyID3

logger = logging.getLogger('core') 

def search_song_by_title(titolo):
    titolo = str(titolo)
    if "VEVO" not in titolo:
        titolo = titolo + " VEVO"
    # Costruisce la stringa di ricerca
    query = f"ytsearch1:{titolo}"  # il "1" limita il risultato al primo video

    # Esegue yt-dlp in JSON mode
    result = subprocess.run(
        ["yt-dlp", "--dump-json", query],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error("Errore durante la ricerca: %s", result.stderr)
        return None

    # Parsing JSON
    video_info = json.loads(result.stdout)
    return video_info.get("webpage_url")

def download_song_details(query,id):
    # Esegue yt-dlp in JSON mode
    result = subprocess.run(
        ["yt-dlp", "--dump-json", query],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logger.error("Errore durante la ricerca: %s", result.stderr)
        return None
    # Parsing JSON
    video_info = json.loads(result.stdout)
    file_path = create_music_folder(video_info.get("title"))
    song_details = create_song_dict(video_info, file_path,id)
    _exit = download_song_locally(file_path, query,song_details) 
    if _exit == 1:
        logger.error("Errore durante il download del brano.")
        return None
    elif _exit == 2:
        return ''
    elif _exit == 0:
        return song_details

def create_song_dict(video_info,file_path,id):
    return {
        "id": id if id is not None else video_info.get("id"),
        "title": video_info.get("title"),
        "artist": video_info.get("uploader"),
        "duration": video_info.get("duration_string"),
        "release_date": video_info.get("upload_date"),
        "cover_image": video_info.get("thumbnail"),
        "url": file_path
    }

def create_music_folder(song_title):
    # Define the specific path to the /music folder
    music_folder = os.getenv("MUSIC_PATH", "./music")
    os.makedirs(music_folder, exist_ok=True)

    song_name = song_title # Replace spaces with underscores
    file_path = os.path.join(music_folder, f"{song_name}")
    return file_path

def download_song_locally(file_path, query,song_details):
    mp3_file_path = file_path.replace(".webm", ".mp3")
    if os.path.isfile(mp3_file_path):
        logger.info(f"Song already exists at {mp3_file_path}")
        return 2

    download_result = subprocess.run(
        [
            "yt-dlp", "--extract-audio", "--audio-format", "mp3",
            "--no-playlist", "--quiet", "--no-warnings", "-o", file_path, query
        ],
        capture_output=True,
        text=True
    )

    if download_result.returncode != 0:
        logger.error("Errore durante il download: %s", download_result.stderr)
        return 1

    try:
        add_tags_to_mp3(mp3_file_path, create_tags(mp3_file_path, song_details))
    except Exception as e:
        logger.error(f"Errore durante l'aggiunta dei tag: {e}")
        return 1

    return 0

def handle_song_search(data):
    from .business_logic import search_song_by_title, download_song_details
    from .serializers import SongSerializer

    logger.debug(f"Received song request for: {data}")
    
    url = search_song_by_title(data['data'])
    song = download_song_details(url)

    if song == '':
        return {"message": "Song already downloaded"}, 409

    if song is None:
        return {"message": "Invalid song data"}, 400

    serializer = SongSerializer(data=song)
    if serializer.is_valid():
        serializer.save()

        return serializer.data, 201
    else:
        return serializer.errors, 400

def handle_url_search(data):
    from .business_logic import search_song_by_title, download_song_details
    from .serializers import SongSerializer

    logger.debug(f"Received song request for: {data}")
    
    song = download_song_details(data['url'],data['id'])

    if song == '':
        return {"message": "Song already downloaded"}, 409

    if song is None:
        return {"message": "Invalid song data"}, 400

    serializer = SongSerializer(data=song)
    if serializer.is_valid():
        serializer.save()

        return serializer.data, 201
    else:
        return serializer.errors, 400

def add_tags_to_mp3(file_path, tags):
    try:
        audio = EasyID3(file_path + '.mp3')
        for tag, value in tags.items():
            if value:  # Verifica che il valore del tag non sia None o vuoto
                audio[tag] = str(value)  # Converti il valore in stringa per evitare errori
            else:
                logger.warning(f"Tag '{tag}' ha un valore non valido: {value}")
        audio.save()
        logger.info(f"Tags aggiunti al file MP3: {file_path}")
    except Exception as e:
        logger.error(f"Errore durante l'aggiunta dei tag: {e}")

def create_tags(file_path,song_details):
    # Assumi che il percorso del file sia nei dati serializzati
    tags = {
            "Title": song_details["title"],
            "Artist": song_details["artist"],
            "Album": song_details["artist"],
            "Date": song_details["release_date"],
        }
    logger.debug(f"Adding tags to MP3 file at {file_path} with tags: {tags}")
    return tags

def delete_song(song_id):
    try:
        song = Song.objects.get(id=song_id)
        file_path = song.url + ".mp3"
        print(f"Attempting to delete song with ID {song_id} at {file_path}")
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"File {file_path} deleted successfully.")
            return 0
        else:
            logger.warning(f"File {file_path} does not exist.")
            return 1
    except Song.DoesNotExist:
        logger.error(f"Song with ID {song_id} does not exist.")
        return 1
    except Exception as e:
        logger.error(f"Error deleting song with ID {song_id}: {e}")
        return 2