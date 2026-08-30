# -*- coding: utf-8 -*-
import os
import subprocess
import re
import urllib.request
import urllib.parse
import yt_dlp
import static_ffmpeg

# Initialize static FFmpeg paths
static_ffmpeg.add_paths()

# Define directories
BASE_DIR = r"D:\菩提缘\新鲜人"
ORIGINAL_DIR = os.path.join(BASE_DIR, "原音频")
REVERSED_DIR = os.path.join(BASE_DIR, "倒放音频")

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(REVERSED_DIR, exist_ok=True)

songs = [
    {"name": "跳楼机", "query": "LBI利比 跳楼机", "start": 81},
    {"name": "玻璃", "query": "Gareth.T 玻璃", "start": 29},
    {"name": "redred", "query": "CORTIS REDRED", "start": 38},
    {"name": "apt", "query": "ROSÉ Bruno Mars APT", "start": 3},
    {"name": "never gonna give you up", "query": "https://youtu.be/dQw4w9WgXcQ?si=cF-Tsj4sa6oEzadF", "start": 0},
    {"name": "恭喜发财", "query": "刘德华 恭喜发财", "start": 6},
    {"name": "甲乙丙丁", "query": "李佳薇 甲乙丙丁", "start": 59},
    {"name": "海屿你", "query": "马也_Crabbit Cole先生 海屿你", "start": 81},
    {"name": "太阳之子", "query": "周杰伦 太阳之子", "start": 38},
    {"name": "海阔天空", "query": "Beyond 海阔天空", "start": 73}
]

def search_bilibili(keyword):
    print(f"[搜索] 正在 Bilibili 搜索: {keyword} ...")
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://search.bilibili.com/all?keyword={encoded_keyword}"
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            bvs = re.findall(r'BV1[0-9a-zA-Z]{9}', html)
            seen = []
            for bv in bvs:
                if bv not in seen:
                    seen.append(bv)
            return seen
    except Exception as e:
        print(f"[警告] Bilibili 搜索失败: {e}")
    return []

def download_audio(name, query, temp_output_path):
    urls = []
    if query.startswith("http://") or query.startswith("https://"):
        urls.append(query)
    else:
        # Try Bilibili first
        bvs = search_bilibili(query)
        if bvs:
            print(f"[发现] 在 Bilibili 找到 {len(bvs)} 个相关视频。尝试下载第一个: {bvs[0]}")
            urls.append(f"https://www.bilibili.com/video/{bvs[0]}")
        
        # Fallback to YouTube search
        urls.append(f"ytsearch1:{query}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_output_path,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }
    
    for url in urls:
        print(f"[下载] 正在尝试从 {url} 下载...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                # Find the downloaded file
                base_dir = os.path.dirname(temp_output_path)
                base_name = os.path.basename(temp_output_path)
                for f in os.listdir(base_dir):
                    if f.startswith(base_name):
                        full_path = os.path.join(base_dir, f)
                        # Check file size: if less than 1MB, it's likely a short preview or meme video, skip it
                        if os.path.getsize(full_path) < 1024 * 1024:
                            print(f"[警告] 下载的视频文件大小过小 ({os.path.getsize(full_path)} 字节)，可能非完整歌曲。跳过并尝试下一个来源。")
                            try:
                                os.remove(full_path)
                            except:
                                pass
                            continue
                        return full_path
            except Exception as e:
                print(f"[错误] 尝试下载 {url} 失败: {e}")
    return None

def reverse_audio(input_path, output_mp3_path, output_wav_path):
    print(f"[转换] 正在生成倒放音频: {input_path} ...")
    
    # 1. Generate reversed MP3
    cmd_mp3 = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "areverse",
        "-q:a", "2",
        output_mp3_path
    ]
    
    # 2. Generate reversed WAV (for maximum compatibility with the web player)
    cmd_wav = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "areverse",
        output_wav_path
    ]
    
    try:
        # Run MP3 conversion
        subprocess.run(cmd_mp3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Run WAV conversion
        subprocess.run(cmd_wav, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[成功] 已生成: {output_mp3_path} 和 {output_wav_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[错误] FFmpeg 转换失败: {e}")
        return False

def convert_to_mp3(input_path, output_mp3_path, start_time=None, duration=10):
    print(f"[转码] 正在将原始音频截取 {duration} 秒副歌并转为 MP3: {input_path} (从 {start_time} 秒开始) ...")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path
    ]
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    cmd.extend([
        "-t", str(duration),
        "-q:a", "2",
        output_mp3_path
    ])
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[错误] FFmpeg 转码 MP3 失败: {e}")
        return False

def main():
    print("开始处理倒放音频任务...")
    for song in songs:
        name = song["name"]
        query = song["query"]
        start_time = song.get("start", 0)
        
        # Check if already processed
        out_mp3 = os.path.join(REVERSED_DIR, f"{name}_倒放.mp3")
        out_wav = os.path.join(REVERSED_DIR, f"{name}_倒放.wav")
        orig_mp3 = os.path.join(ORIGINAL_DIR, f"{name}.mp3")
        
        if os.path.exists(out_mp3) and os.path.exists(out_wav) and os.path.exists(orig_mp3):
            print(f"\n[跳过] {name} 已经存在完整的原音频和倒放音频，无需重复处理。")
            continue
            
        # Temp base filename without extension
        temp_path = os.path.join(ORIGINAL_DIR, f"{name}_temp")
        
        # Clean up existing temp files first
        for f in os.listdir(ORIGINAL_DIR):
            if f.startswith(f"{name}_temp"):
                try:
                    os.remove(os.path.join(ORIGINAL_DIR, f))
                except:
                    pass
        
        # Download
        downloaded_file = download_audio(name, query, temp_path)
        if downloaded_file:
            print(f"[已下载] 临时文件保存至: {downloaded_file}")
            
            # Convert downloaded file to standard orig_mp3 (cut to 10s chorus)
            success_conv = convert_to_mp3(downloaded_file, orig_mp3, start_time=start_time, duration=10)
            
            # Clean up the downloaded temporary file if it's not the final mp3 itself
            if downloaded_file != orig_mp3:
                try:
                    os.remove(downloaded_file)
                except:
                    pass
            
            if success_conv and os.path.exists(orig_mp3):
                print(f"[成功] 原音频已保存为: {orig_mp3}")
                # Reverse
                reverse_audio(orig_mp3, out_mp3, out_wav)
            else:
                print(f"[错误] 无法转码 {name} 的原始音频。")
        else:
            print(f"[警告] 无法为 {name} 下载音频。")

if __name__ == "__main__":
    main()
