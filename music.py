import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
import yt_dlp
import os

# Spotify API Kimlik Bilgileri
SPOTIPY_CLIENT_ID = "SPOTIPY_CLIENT_ID"
SPOTIPY_CLIENT_SECRET = "SPOTIPY_CLIENT_SECRET"

# Spotify bağlantısını kur
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

def get_playlist_tracks(playlist_url):
    """ Spotify playlist linkindeki şarkıları alır """
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    songs = []
    
    for item in results['items']:
        track = item['track']
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        duration_ms = track['duration_ms']  # Şarkının süresi
        duration_sec = duration_ms / 1000   # Milisaniyeyi saniyeye çevir
        songs.append({"name": f"{song_name} {artist_name}", "duration": duration_sec})
    
    return songs

def search_youtube(query):
    """ YouTube'da şarkıyı arayıp en uygun videonun URL'sini döndürür """
    results = YoutubeSearch(query, max_results=1).to_dict()
    if results:
        return "https://www.youtube.com" + results[0]['url_suffix']
    return None

def estimate_total_size(songs, bitrate=192):
    """ Şarkı sürelerine göre toplam tahmini dosya boyutunu hesaplar (MB cinsinden) """
    total_size = 0
    for song in songs:
        duration_sec = song["duration"]
        size_mb = (bitrate * 1000 / 8) * duration_sec / (1024 * 1024)  # Byte → MB dönüşümü
        total_size += size_mb
    return round(total_size, 2)

def download_audio(youtube_url, output_folder="downloads"):
    """ YouTube videosunu en iyi ses kalitesinde indirir """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def main():
    playlist_url = input("Spotify Playlist URL: ")
    songs = get_playlist_tracks(playlist_url)
    
    # Toplam tahmini dosya boyutunu hesapla
    total_size_mb = estimate_total_size(songs)
    print(f"\nToplam tahmini dosya boyutu: {total_size_mb} MB")
    
    # Kullanıcıdan izin al
    izin = input("Şarkıları indirmek istiyor musunuz? (E/H): ").strip().lower()
    if izin != 'e':
        print("İndirme işlemi iptal edildi.")
        return

    # İndirme işlemi başlıyor
    for song in songs:
        print(f"Şarkı aranıyor: {song['name']}")
        youtube_url = search_youtube(song["name"])
        if youtube_url:
            print(f"İndiriliyor: {youtube_url}")
            download_audio(youtube_url)
        else:
            print(f"Bulunamadı: {song['name']}")

    print("Tüm şarkılar indirildi!")

if __name__ == "__main__":
    main()
