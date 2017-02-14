from subprocess import call


def upload(title, description, filename):
    title_option = '--title="{}"'.format(title)
    description_option = '--description=\'{}\''.format(description.encode('string-escape'))
    category_option = '--category=Gaming'
    tags_option = '--tags="spel"'
    language_option = '--default-language="sv"'
    audio_language_option = '--default-audio-language="sv"'
    client_secret_option = '--client-secrets=cs.json' 
    commands = ["python", "yu/bin/youtube-upload", title_option, description_option, category_option, 
            tags_option, language_option, audio_language_option, client_secret_option, filename]

    command = " ".join(commands) 
    call(command, shell=True)
