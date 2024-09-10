import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import google_auth_oauthlib.flow 
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime, timedelta
import re


# Your API key
API_KEY = os.environ.get("YOUTUBE_API_KEY") 
YOUTUBE_SECRETS_PATH = os.environ.get("YOUTUBE_SECRETS_PATH") 
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID") 
def episode_url_lookup():
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        # Replace with the ID of the channel you want to fetch videos from
        channel_id = YOUTUBE_CHANNEL_ID
        # Get the uploads playlist ID
        channels_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        lookup = {}
        for channel in channels_response["items"]:
            uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

            print(f"Videos in channel {channel_id}")

            # Retrieve the list of videos uploaded to the channel
            playlistitems_list_request = youtube.playlistItems().list(
                playlistId=uploads_list_id,
                part="snippet",
                maxResults=50
            )
            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()

                # Print information about each video.
                for playlist_item in playlistitems_list_response["items"]:
                    title = playlist_item["snippet"]["title"]
                    video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"{title} ({video_url})")
                    match = re.match(r'^(\d+)', title)
                    if match:
                        episode_number = int(match.group(1))
                        lookup[episode_number] = video_url

                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request, playlistitems_list_response)

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
    return lookup

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

youtube = None

def upload_video(title, description, tags, publish_date, video_path):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    global youtube
    if youtube is None:
        client_secrets_file = YOUTUBE_SECRETS_PATH
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                client_secrets_file, scopes )
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                
        # This will provide the authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
                
        print(f'Please go to this URL: {auth_url}')
        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)
                
        credentials = flow.credentials

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)


    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "20", # Shorts
                "defaultAudioLanguage": "sv",
                "defaultLanguage": "sv",
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_date,
                'selfDeclaredMadeForKids':False
            }
        },
        media_body=googleapiclient.http.MediaFileUpload(video_path)
    )
    response = request.execute()

    print(f'Video id "{response["id"]}" was successfully uploaded and scheduled for {publish_date}.')


if __name__ == "__main__":
    lookup = episode_url_lookup()
    print(lookup)