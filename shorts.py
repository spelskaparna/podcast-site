# %%
from dataclasses import dataclass
import os
import re
from episode_parser import extract_meta_data
import youtube_test
from datetime import datetime, timedelta
import pandas as pd
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
records = []
for i, video_file in enumerate(video_files):
    print(i)
    if i not in range(3,6):
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
    start_date = datetime(2024, 9, 13)
    publish_date = (datetime.now() + timedelta(days=i)).isoformat() + 'Z'
    # related_video_url = url_lookup[number]
    record = {"number":number,"title":title, "description":description, "TikTok":f"{title} \n {description}"}
    records.append(record)
    youtube_test.upload_video(title, description, tags, publish_date, video_path)
df = pd.DataFrame.from_records(records)
df.to_csv("teasers.csv")