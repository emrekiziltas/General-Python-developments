import requests
import time
import subprocess
import os
import tempfile
import soundfile as sf
import numpy as np

API_KEY = "AIzaSyBCxfAeeLs0KLhGaxdTBam-ENfOY6wNxxE"
CHANNEL_HANDLE = "@iniseminarroom2"

def get_channel_id(handle):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={API_KEY}"
    r = requests.get(url)
    data = r.json()
    if data.get("items"):
        return data["items"][0]["id"]
    else:
        raise ValueError("Kanal bulunamadı.")

def get_live_video(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={API_KEY}"
    r = requests.get(url)
    data = r.json()
    items = data.get("items", [])
    if items:
        return items[0]["id"]["videoId"]
    return None

def has_audio_from_stream(video_id):
    """YouTube canlı yayınından 10 saniyelik ses örneği alır ve analiz eder."""
    tmp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_mp3_name = tmp_mp3.name
    tmp_mp3.close()

    # ffmpeg ile 10 saniyelik ses örneği al
    stream_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", stream_url, "-t", "10", "-vn", "-ac", "1", "-ar", "16000", tmp_mp3_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception as e:
        print("❌ FFmpeg ile canlı yayın sesi alınamadı:", e)
        return False

    # Geçici WAV’a dönüştür ve ses kontrolü yap
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_wav_name = tmp_wav.name
    tmp_wav.close()

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3_name, tmp_wav_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        data, samplerate = sf.read(tmp_wav_name)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        volume = np.mean(np.abs(data))
        os.remove(tmp_mp3_name)
        os.remove(tmp_wav_name)
    except Exception as e:
        print("❌ Ses örneği okunamadı:", e)
        return False

    if volume > 0.001:
        print(f"🔊 Ses var (ortalama genlik: {volume:.6f})")
        return True
    else:
        print(f"🤫 Sessizlik (ortalama genlik: {volume:.6f})")
        return False


def main():
    channel_id = get_channel_id(CHANNEL_HANDLE)
    print(f"Kanal ID: {channel_id}")

    while True:
        video_id = get_live_video(channel_id)
        if video_id:
            print(f"🔴 Kanal şu anda CANLI! (Video ID: {video_id})")
            has_audio_from_stream(video_id)
        else:
            print("⚪ Şu anda canlı yayın yok.")
        time.sleep(5)  # Her 1 dakikada bir kontrol

if __name__ == "__main__":
    main()
