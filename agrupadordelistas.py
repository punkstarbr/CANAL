import requests
import subprocess
import os
from bs4 import BeautifulSoup
import re


def search_image_url(channel_name):
    query = f"{channel_name} logo filetype:png OR filetype:jpg"
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        img_tags = soup.find_all("img")
        
        for img_tag in img_tags:
            img_url = img_tag["src"]
            if re.match(r'^https?://', img_url):
                return img_url
                
    return None

def is_channel_working(url, headers=None):
    try:
        cmd = [
            "ffmpeg",
            "-headers",
            f"User-Agent: {headers['User-Agent']}" if headers and "User-Agent" in headers else "User-Agent: python-requests/2.25.1",
            "-i",
            url,
            "-t",
            "10",
            "-f",
            "null",
            "-"
        ]

        process = subprocess.run(cmd, stderr=subprocess.PIPE, universal_newlines=True, timeout=5)
        return process.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False

repo_urls = [
    "https://github.com/punkstarbr/STR-YT/raw/main/LISTA%20%20ESTADOS%20UNIDOS.M3U"
]

working_channels = []

for url in repo_urls:
    m3u_response = requests.get(url)

    if m3u_response.status_code == 200:
        m3u_lines = m3u_response.text.splitlines()

        for i, line in enumerate(m3u_lines):
            if line.startswith("#EXTM3U"):
                working_channels.append({"extm3u_line": line})
            elif line.startswith("#EXTINF"):
                extinf_line = line
                extvlcopt_line = None
                kodiprop_lines = []
                stream_url = None
                headers = {}

                for j in range(i + 1, len(m3u_lines)):
                    next_line = m3u_lines[j]

                    if next_line.startswith("#EXTVLCOPT"):
                        extvlcopt_line = next_line
                        if "http-user-agent" in extvlcopt_line:
                            user_agent = extvlcopt_line.split("=")[1]
                            headers["User-Agent"] = user_agent
                    elif next_line.startswith("#KODIPROP"):
                        kodiprop_lines.append(next_line)
                    elif not next_line.startswith("#"):
                        stream_url = next_line
                        break

                if stream_url:
                    should_add_channel = is_channel_working(stream_url, headers) or stream_url.startswith("https://video-auth") or stream_url.startswith("https://d1zx6l1dn8vaj5.cloudfront.net/out/v1/b89cc37caa6d418eb423cf092a2ef970")
                    if should_add_channel:
                        working_channels.append({
                            "extinf_line": extinf_line,
                            "extvlcopt_line": extvlcopt_line,
                            "kodiprop_lines": kodiprop_lines,
                            "stream_url": stream_url
                        })


with open("LISTA ESTADOS UNIDOS.M3U", "w") as f:
    for channel in working_channels:
        if "extm3u_line" in channel:
            f.write(f"{channel['extm3u_line']}\n")
        else:
            extinf_line_parts = channel['extinf_line'].split(',', 1)
            channel_info = extinf_line_parts[0].strip()
            channel_name = extinf_line_parts[1].strip()

            if "tvg-logo" not in channel_info or 'tvg-logo=""' in channel_info or 'tvg-logo="N/A"' in channel_info:
                image_url = search_image_url(channel_name)
                if image_url:
                    if "tvg-logo" not in channel_info:
                        channel_info += f' tvg-logo="{image_url}"'
                    else:
                        channel_info = channel_info.replace('tvg-logo=""', f'tvg-logo="{image_url}"')
                        channel_info = channel_info.replace('tvg-logo="N/A"', f'tvg-logo="{image_url}"')

            channel['extinf_line'] = f"{channel_info},{channel_name}"

            f.write(f"{channel['extinf_line']}\n")
            if channel['extvlcopt_line']:
                f.write(f"{channel['extvlcopt_line']}\n")
            for kodiprop_line in channel['kodiprop_lines']:
                f.write(f"{kodiprop_line}\n")
            f.write(f"{channel['stream_url']}\n")

            
         
                        
