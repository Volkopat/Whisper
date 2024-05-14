
from __future__ import unicode_literals
from pytube import YouTube, Playlist
import whisper
import os

def GetPlaylist(playlist_url):
    print("Fetching videos from playlist: %s" % playlist_url)
    try:
        playlist = Playlist(playlist_url)
        video_urls = list(playlist.video_urls)
        print("Found %s videos in playlist." % len(video_urls))
        return video_urls
    except Exception as e:
        print("An error occurred while fetching playlist videos: %s" % e)
        return []

def DownloadVideo(video_url, output_path):
    print("Downloading video: %s" % video_url)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        video = YouTube(video_url)
        stream = video.streams.get_highest_resolution()
        video_file_path = stream.download(output_path=output_path)
        print("Video downloaded successfully: %s" % video_file_path)
        return video_file_path
    except Exception as e:
        print("An error occurred while downloading video: %s" % e)
        return None

def WhisperTranscribe(video_file_path):
    print("Transcribing video file: %s" % video_file_path)
    model = whisper.load_model("large")

    try:
        result = model.transcribe(video_file_path)
        print("Transcription completed successfully.")
        return result["text"]
    except Exception as e:
        print("An error occurred during transcription: %s" % e)
        return ""

def Save2MD(transcribed_text, output_dir, md_file_name):
    print("Saving transcription to Markdown file: %s.md" % md_file_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    md_file_path = os.path.join(output_dir, "%s.md" % md_file_name)

    try:
        with open(md_file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(transcribed_text)
        print("Transcription saved successfully to %s" % md_file_path)
    except Exception as e:
        print("An error occurred while saving the transcription: %s" % e)

def main(playlist_url, name):
    video_urls = GetPlaylist(playlist_url)

    for idx, video_url in enumerate(video_urls, start=1):
        print("Processing video %s/%s: %s" % (idx, len(video_urls), video_url))
        try:
            video = YouTube(video_url)
            video_title = video.title
            sanitized_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()

            output_dir = os.path.join("output", name, sanitized_title)
            video_file_path = DownloadVideo(video_url, output_dir)

            if video_file_path:
                transcribed_text = WhisperTranscribe(video_file_path)
                Save2MD(transcribed_text, output_dir, sanitized_title)

                os.remove(video_file_path)

        except Exception as e:
            print("An error occurred processing video %s: %s" % (video_url, e))

if __name__ == "__main__":
    playlist_url = ["https://www.youtube.com/playlist?list=PLpOGQvPCDQzsWvT_bqmexrJ359RTQQuMO",
                    "https://www.youtube.com/playlist?list=PLoROMvodv4rPLKxIpqhjhPgdQy7imNkDn"]
    name = ["Pattern Recognition [PR] Lecture Winter 20/21",
            "Stanford CS224W: Machine Learning with Graphs"]
    for i in range(len(playlist_url)):
        main(playlist_url[i], name[i])
