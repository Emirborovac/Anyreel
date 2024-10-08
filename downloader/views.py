import os
import yt_dlp
import instaloader
import requests
from django.shortcuts import render
from django.http import HttpResponse
from .forms import VideoDownloadForm
from pathlib import Path
import re

# Define the download folder
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

# Define the paths to the cookies files
YOUTUBE_COOKIES_FILE = 'www.youtube.com_cookies.txt'
INSTAGRAM_COOKIES_FILE = 'www.instagram.com_cookies.txt'

def get_video_title(url, cookies_file=None):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': cookies_file,  # Use the specified cookies file
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'unknown_video')
    return title

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube_video(url, download_folder):
    unique_filename = get_video_title(url, cookies_file=YOUTUBE_COOKIES_FILE)
    sanitized_filename = sanitize_filename(unique_filename)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(download_folder, f'{sanitized_filename}.%(ext)s'),
        'noplaylist': True,
        'nocache': True,
        'cookiefile': YOUTUBE_COOKIES_FILE,  # Use the YouTube cookies file
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get('duration', 0)
            if duration < 5 or duration > 120:
                return None, f"Video duration is {duration} seconds, which is outside the allowed range."
            
            ydl.download([url])
            video_path = os.path.join(download_folder, f'{sanitized_filename}.mp4')
            if os.path.exists(video_path):
                return video_path, None
            else:
                return None, "Failed to find the downloaded video file."
    except Exception as e:
        return None, f"Failed to download YouTube video: {e}"

def download_other_video(url, download_folder):
    unique_filename = get_video_title(url, cookies_file=YOUTUBE_COOKIES_FILE)
    sanitized_filename = sanitize_filename(unique_filename)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(download_folder, f'{sanitized_filename}.%(ext)s'),
        'noplaylist': True,
        'cookiefile': YOUTUBE_COOKIES_FILE,  # Use the YouTube cookies file
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get('duration', 0)
            if duration < 5 or duration > 120:
                return None, f"Video duration is {duration} seconds, which is outside the allowed range."
            ydl.download([url])
            video_path = os.path.join(download_folder, f'{sanitized_filename}.mp4')
            if os.path.exists(video_path):
                return video_path, None
            else:
                return None, "Failed to find the downloaded video file."
    except Exception as e:
        return None, str(e)
        
import instaloader
import os
import requests
from instaloader.exceptions import LoginRequiredException, ConnectionException

def download_instagram_reel(reel_url, download_folder):
    try:
        L = instaloader.Instaloader()

        # Log message to check if we're inside the try block
        print("Initializing Instaloader and checking session file...")

        # Define the path to the session file
        session_file = r"session.session"
        
        # Check if the session file exists and load it using the correct method
        if os.path.exists(session_file):
            L.load_session_from_file('amircharitymill', session_file)
            print(f"Session loaded successfully from {session_file}.")
        else:
            print(f"Session file '{session_file}' not found.")
            return None, f"Session file '{session_file}' not found."

        # Ensure the download folder exists
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
            print(f"Download folder created at {download_folder}.")

        # Extract shortcode from the reel URL
        print("Extracting shortcode from the reel URL...")
        shortcode = reel_url.split("/")[-2]
        
        # Get the post object using the shortcode
        print(f"Fetching the post using shortcode: {shortcode}")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Get the video URL
        video_url = post.video_url
        print(f"Video URL found: {video_url}")

        # Generate a unique filename for the video
        unique_filename = sanitize_filename(post.title if post.title else shortcode)
        video_path = os.path.join(download_folder, f"{unique_filename}.mp4")
        
        if video_url:
            print(f"Downloading video to {video_path}...")
            response = requests.get(video_url, stream=True)
            with open(video_path, 'wb') as video_file:
                for chunk in response.iter_content(chunk_size=8192):
                    video_file.write(chunk)
            print("Download completed successfully.")
            return video_path, None
        else:
            print("No video found in the post.")
            return None, "No video found in the post."

    except LoginRequiredException as login_err:
        print(f"Login required: {str(login_err)}")
        return None, f"Login required: {str(login_err)}"
    except ConnectionException as conn_err:
        print(f"Connection error: {str(conn_err)}")
        return None, f"Connection error: {str(conn_err)}"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None, f"Unexpected error: {str(e)}"


def download_video(request):
    if request.method == 'POST':
        form = VideoDownloadForm(request.POST)
        if form.is_valid():
            video_type = form.cleaned_data['video_type']
            url = form.cleaned_data['url']
            download_folder = DOWNLOAD_FOLDER

            if video_type == '1':
                video_path, error = download_youtube_video(url, download_folder)
            elif video_type == '2':
                video_path, error = download_instagram_reel(url, download_folder)
            elif video_type == '3':
                video_path, error = download_other_video(url, download_folder)
            else:
                error = "Invalid video type selected."

            if video_path:
                with open(video_path, 'rb') as video_file:
                    response = HttpResponse(video_file.read(), content_type='video/mp4')
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(video_path)}'
                    return response
            else:
                return render(request, 'downloader/index.html', {'form': form, 'error': error})
    else:
        form = VideoDownloadForm()
    return render(request, 'downloader/index.html', {'form': form})
