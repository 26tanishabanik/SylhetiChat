import os
import subprocess
import sys
import glob
import shutil
from pydub import AudioSegment

def download_youtube_video(video_url, output_directory):
    command = [
        'yt-dlp',
        '-o', os.path.join('/content/output/audio/', '%(title)s.%(ext)s'),
        '-x',
        '--audio-format', 'wav',
        video_url
    ]
    subprocess.run(command)

def download_facebook_video(video_url, output_directory):
    command = [
        'facebook_downloader',
        video_url,
        '-o', '/content/output/videos/',
        '-a'
    ]
    subprocess.run(command)

# Function to extract audio from video and save as WAV
def extract_audio(video_path, output_audio_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        output_audio_path
    ]
    subprocess.run(command)

def normalize_audio_frequency(path, ext):
    command = [
        'bash', '/content/output/normalize_sr.sh', path, ext
    ]
    subprocess.run(command)
    os.remove(path)

# Function to convert audio to 16kHz if needed
def convert_to_16khz(audio_path):
    audio = AudioSegment.from_file(audio_path)
    if audio.frame_rate != 16000:
        print("Before conversion, audio frequency", audio.frame_rate)
        temp_path = f"{audio_path}.wav"
        command = [
            'ffmpeg',
            '-loglevel', 'warning',
            '-hide_banner',
            '-stats',
            '-i', audio_path,
            '-ar', '16000',
            '-ac', '1',
            temp_path
        ]
        subprocess.run(command)
        os.remove(audio_path)
        os.rename(temp_path, audio_path)
        print("After conversion, audio frequency", audio.frame_rate)

def remove_spaces_from_filename(audio_path):
    print("Old Audio path: ", audio_path)
    new_audio_path = audio_path.replace(' ', '')
    print("New Audio path: ", new_audio_path)
    os.rename(audio_path, new_audio_path)
    return new_audio_path


# Function to split audio into 25-second clips
def split_audio(audio_path, output_directory):
    audio = AudioSegment.from_wav(audio_path)
    duration_ms = len(audio)
    clip_duration = 25 * 1000
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    for i in range(0, duration_ms, clip_duration):
        clip = audio[i:i + clip_duration]
        clip.export(os.path.join(output_directory, f"{base_filename}_clip_{i // clip_duration:03d}.wav"), format="wav")

if __name__ == "__main__":
    # Check if ffmpeg is installed
    if not shutil.which("ffmpeg"):
        print("Please install ffmpeg.")
        sys.exit(1)

    videos = []
    base_output_directory = "output"
    videos_output_directory = os.path.join(base_output_directory, "videos")
    audio_output_directory = os.path.join(base_output_directory, "audio")
    clips_output_directory = os.path.join(base_output_directory, "audio_clips")

    # Create output directories
    os.makedirs(videos_output_directory, exist_ok=True)
    os.makedirs(audio_output_directory, exist_ok=True)
    os.makedirs(clips_output_directory, exist_ok=True)

    for video_url in videos:
      if "facebook" in video_url:
        download_facebook_video(video_url, videos_output_directory)
      else:
        download_youtube_video(video_url, audio_output_directory)

      # Extract audio from the downloaded video
      if "youtube" in video_url:
        for audio_file in glob.glob(os.path.join(audio_output_directory, "*.wav")):
          if "16kHz" not in audio_file:
            audio_path = remove_spaces_from_filename(audio_file)
            normalize_audio_frequency(audio_path, "wav")
      else:
        for video_file in glob.glob(os.path.join(videos_output_directory, "*.mp4")):
          video_filename = os.path.basename(video_file)
          audio_filename = f"{os.path.splitext(video_filename)[0]}.wav"
          audio_path = os.path.join(audio_output_directory, audio_filename)
          audio_path = audio_path.replace(' ', '')
          extract_audio(video_file, audio_path)
          normalize_audio_frequency(audio_path, "wav")
      for audio_file in glob.glob(os.path.join(audio_output_directory, "*.wav")):         
        split_audio(audio_file, clips_output_directory)
      print("All operations completed.")
        
