import os
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if YOUTUBE_API_KEY:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
else:
    youtube = None


def fetch_youtube_videos(query: str, max_results: int = 3):
    if youtube is None:
        return [{"error": "YouTube API key not configured"}]

    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order="relevance"
        )
        response = request.execute()

        videos = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            videos.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })

        return videos

    except Exception as e:
        return [{"error": str(e)}]