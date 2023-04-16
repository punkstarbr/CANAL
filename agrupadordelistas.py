import requests

repo_urls = [    "https://api.github.com/repos/punkstarbr/STR-YT/contents",    "https://api.github.com/repos/punkstarbr/YT2M3U/contents",   "https://api.github.com/repos/punkstarbr/STR3/contents",  "https://api.github.com/repos/punkstarbr/STR2/contents"]

lists = []
for url in repo_urls:
    response = requests.get(url)

    if response.status_code == 200:
        contents = response.json()
        m3u_files = [content for content in contents if content["name"].endswith(".m3u")]

        for m3u_file in m3u_files:
            m3u_url = m3u_file["download_url"]
            m3u_response = requests.get(m3u_url)

            if m3u_response.status_code == 200:
                lists.append((m3u_file["name"], m3u_response.text))
    else:
        print(f"Error retrieving contents from {url}")

lists = sorted(lists, key=lambda x: x[0])

with open("lista1.M3U", "w") as f:
    for l in lists:
        f.write(l[1])            

        
        
        
import requests

def is_channel_working(url, headers=None):
    try:
        response = requests.head(url, timeout=5, headers=headers)
        return response.status_code in (200, 206)
    except requests.exceptions.RequestException:
        return False

repo_urls = [
    "https://api.github.com/repos/punkstarbr/STR3/contents",
    "https://api.github.com/repos/free-greek-iptv/greek-iptv/contents"
]

working_channels = []

for url in repo_urls:
    response = requests.get(url)

    if response.status_code == 200:
        contents = response.json()
        m3u_files = [content for content in contents if content["name"].endswith(".m3u")]

        for m3u_file in m3u_files:
            m3u_url = m3u_file["download_url"]
            m3u_response = requests.get(m3u_url)

            if m3u_response.status_code == 200:
                m3u_lines = m3u_response.text.splitlines()

                for i, line in enumerate(m3u_lines):
                    if line.startswith("#EXTINF"):
                        extinf_line = line
                        extvlcopt_line = None
                        kodiprop_lines = []
                        stream_url = None
                        headers = {}

                        # Iterate through the next lines
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
                            if is_channel_working(stream_url, headers):
                                working_channels.append({
                                    "extinf_line": extinf_line,
                                    "extvlcopt_line": extvlcopt_line,
                                    "kodiprop_lines": kodiprop_lines,
                                    "stream_url": stream_url
                                })

# Write working channels to a new .m3u file
with open("lista2.M3U", "w") as f:
    f.write("#EXTM3U\n")
    for channel in working_channels:
        f.write(f"{channel['extinf_line']}\n")
        if channel['extvlcopt_line']:
            f.write(f"{channel['extvlcopt_line']}\n")
        for kodiprop_line in channel['kodiprop_lines']:
            f.write(f"{kodiprop_line}\n")
        f.write(f"{channel['stream_url']}\n")
                    

            
            
import requests

def is_channel_working(url, headers=None):
    try:
        response = requests.head(url, timeout=10, headers=headers)
        return response.status_code in (200, 206)
    except requests.exceptions.RequestException:
        return False

repo_urls = [
    "https://github.com/punkstarbr/STR-YT/raw/main/REALITY'SLIVE.m3u"
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

                # Iterate through the next lines
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
                    if is_channel_working(stream_url, headers):
                        working_channels.append({
                            "extinf_line": extinf_line,
                            "extvlcopt_line": extvlcopt_line,
                            "kodiprop_lines": kodiprop_lines,
                            "stream_url": stream_url
                        })

with open("lista3.M3U", "w") as f:
    for channel in working_channels:
        if "extm3u_line" in channel:
            f.write(f"{channel['extm3u_line']}\n")
        else:
            f.write(f"{channel['extinf_line']}\n")
            if channel['extvlcopt_line']:
                f.write(f"{channel['extvlcopt_line']}\n")
            for kodiprop_line in channel['kodiprop_lines']:
                f.write(f"{kodiprop_line}\n")
            f.write(f"{channel['stream_url']}\n")
            
            
            
import requests
import subprocess

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
    "https://github.com/LITUATUI/M3UPT/raw/main/M3U/M3UPT.m3u"
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
                    if is_channel_working(stream_url, headers):
                        working_channels.append({
                            "extinf_line": extinf_line,
                            "extvlcopt_line": extvlcopt_line,
                            "kodiprop_lines": kodiprop_lines,
                            "stream_url": stream_url
                        })

with open("lista4.M3U", "w") as f:
    for channel in working_channels:
        if "extm3u_line" in channel:
            f.write(f"{channel['extm3u_line']}\n")
        else:
            f.write(f"{channel['extinf_line']}\n")
            if channel['extvlcopt_line']:
                f.write(f"{channel['extvlcopt_line']}\n")
            for kodiprop_line in channel['kodiprop_lines']:
                f.write(f"{kodiprop_line}\n")
            f.write(f"{channel['stream_url']}\n")            

            
