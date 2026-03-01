from googleapiclient.discovery import build

API_KEY = "YOUR_API_KEY_HERE"

def get_youtube_videos(topic):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.search().list(
        q=topic,
        part="snippet",
        type="video",
        maxResults=5
    )
    response = request.execute()

    videos = []
    for item in response["items"]:
        videos.append({
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
        })

    return videos
