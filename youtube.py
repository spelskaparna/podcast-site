import episode_parser as ep
from subprocess import call
import to_youtube

def add_footer(description):
    with open('youtube_footer') as f:
        footer = f.read()
        description = '{}\n\n{}'.format(description,footer)
    return description 

def upload_episode(n):
    title = ep.extract_title(n)
    description = ep.extract_description_text(n)
    date = ep.extract_date(n)
    url = ep.extract_url(n)
    filename = '{}.mp3'.format(n)
    download(url, filename)
    output = '{}.mp4'.format(n)
    convert_mp3(filename, output)
    description = add_footer(description)
    print(description)
    tags = ep.extract_tags(n)
    print(tags)
    to_youtube.upload(title, description, tags,output)

def convert_mp3(filename, output):
    command = 'ffmpeg -loop 1 -i static/img/frame.jpg -i {} -shortest -b 1000k -acodec copy {}'.format(filename, output)
    call(command, shell=True)

def download(url, filename):
    command = 'wget -O {} {}'.format(filename, url)
    call(command, shell=True)

def test(n):
    title = ep.extract_title(n)
    description = ep.extract_description_text(n)
    print("")
    print(title)
    print(description)

if __name__ == "__main__":
    #upload_episode(n)
    for n in range(26,27):
        upload_episode(n)

