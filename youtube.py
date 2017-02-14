import episode_parser as ep
from subprocess import call
import to_youtube

def upload_episode(n):
    title = ep.extract_title(n)
    description = ep.extract_description_text(n)
    date = ep.extract_date(n)
    url = ep.extract_url(n)
    filename = '{}.mp3'.format(n)
    download(url, filename)
    output = '{}.mp4'.format(n)
    #convert_mp3(filename, output)
    output = 'out.mp4'
    print(description)
    to_youtube.upload(title, description, output)

def convert_mp3(filename, output):
    command = 'ffmpeg -loop 1 -i static/img/logga.png -i {} -shortest -b 1000k -acodec copy {}'.format(filename, output)
    call(command, shell=True)

def download(url, filename):
    command = 'wget -O {} {}'.format(filename, url)
    call(command, shell=True)

if __name__ == "__main__":
    n = 23
    upload_episode(n)
