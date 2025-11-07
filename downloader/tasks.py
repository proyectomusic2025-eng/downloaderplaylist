import os, subprocess, sys, time, zipfile
from celery import shared_task
from django.conf import settings
from .models import DownloadRecord, UserProfile
@shared_task(bind=True)
def download_task(self, user_id, url):
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {'ok': False, 'error': 'Usuario no existe'}
    downloads_dir = os.path.join(settings.MEDIA_ROOT, 'downloads', str(int(time.time())))
    os.makedirs(downloads_dir, exist_ok=True)
    # Try to use local spotify_downloader if present
    try:
        from .spotify_downloader import download_spotify_track
        # If it's a playlist, assume function can download multiple files into downloads_dir
        path = download_spotify_track(url, downloads_dir)
    except Exception as e:
        outtmpl = os.path.join(downloads_dir, "%(title)s.%(ext)s")
        cmd = [sys.executable, '-m', 'spotdl', url, '--output', outtmpl, '--format', 'mp3', '--overwrite', 'skip']
        try:
            subprocess.run(cmd, check=True, timeout=900)
        except subprocess.CalledProcessError as e:
            return {'ok': False, 'error': f'Error en spotdl: {e}'}
        except subprocess.TimeoutExpired:
            return {'ok': False, 'error': 'Timeout en descarga'}
    # collect mp3 files and limit to 3
    mp3s = [os.path.join(downloads_dir, f) for f in os.listdir(downloads_dir) if f.lower().endswith('.mp3')]
    if not mp3s:
        return {'ok': False, 'error': 'No se generó MP3'}
    mp3s_sorted = sorted(mp3s, key=os.path.getmtime)
    selected = mp3s_sorted[:3]
    # create zip
    zip_path = os.path.join(settings.MEDIA_ROOT, 'results', f'result_{int(time.time())}.zip')
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for f in selected:
            zf.write(f, arcname=os.path.basename(f))
            DownloadRecord.objects.create(user=user, title=os.path.basename(f), source_url=url)
    # increment user's download counter by number of tracks delivered
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.downloads_used += len(selected)
    profile.save()
    return {'ok': True, 'path': zip_path, 'title': os.path.basename(zip_path)}
