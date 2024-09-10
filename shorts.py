# %%
from dataclasses import dataclass
import os
import re
from episode_parser import extract_meta_data
import youtube_test
from datetime import datetime, timedelta
path = os.environ.get("TEASER_PATH")
files = os.listdir(path)

# %%
@dataclass
class VideoFile:
    number : int
    video_path : str



video_files = []
for file in files:
    match = re.match(r'^(\d+)', file)
    if match:
        number = int(match.group(1))
        video_path = os.path.join(path, file)
        video_files.append(VideoFile(number, video_path))
# %%
# url_lookup = youtube_test.episode_url_lookup()
# %%
for i, video_file in enumerate(video_files):
    if i != 2:
        continue
    number = video_file.number
    video_path = video_file.video_path
    name, occupation, company, subtitle = extract_meta_data(number)
    if subtitle is None:
        subtitle = f"{occupation} | {company}"
    title = f"Spelskaparna - {number} - {name} ({subtitle})"
    print(f"Uploading:  - {title}")
    description = "Hela avsnittet: https://pod.link/1084993748l \n\n #podcast #gaming #gamedev #gamedevelopment #gamedevlife #indiegamedev"
    tags = ["indiedev", "gamedev"]
    start_date = datetime(2024, 9, 12)
    publish_date = (datetime.now() + timedelta(days=i)).isoformat() + 'Z'
    # related_video_url = url_lookup[number]

    youtube_test.upload_video(title, description, tags, publish_date, video_path)