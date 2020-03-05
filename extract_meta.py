from episode_parser import extract_meta_data
import os
import json

dir_path = os.path.join('content', 'episode')

episodes = {}

for file in os.listdir(dir_path):
    filename = os.fsdecode(file)
    if filename.endswith(".md"):
        episode = int(filename.replace(".md",""))
        name, occupation, company, subtitle = extract_meta_data(episode)
        if subtitle is None:
            subtitle = f"{occupation} | {company}"
        episodes[episode] = {'name':name, 'subtitle':subtitle}

titles = [] 

keys = list(episodes.keys())
keys.sort()
episode_list = []
for key in keys:
    item = episodes[key]
    title = f"{key} {item['name']} {item['subtitle']}"
    titles.append(title)
    episode_list.append(item)



j = json.dumps({'episodes':episode_list, 'titles':titles})
with open("settings.json","w") as f:
    f.write(j)