
import json
import os
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]
HANDLE = "dailyshorts6363"
BASE = "https://www.googleapis.com/youtube/v3"


def api_get(endpoint, params):
    params["key"] = API_KEY
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "DailyShortsBot/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    channel_data = api_get("channels", {
        "part": "snippet,contentDetails,statistics",
        "forHandle": HANDLE,
    })

    channels = channel_data.get("items", [])
    if not channels:
        raise RuntimeError("Could not find the channel handle.")

    channel = channels[0]
    uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist = api_get("playlistItems", {
        "part": "snippet,contentDetails",
        "playlistId": uploads_id,
        "maxResults": 10,
    })

    video_ids = [
        item["contentDetails"]["videoId"]
        for item in playlist.get("items", [])
    ]

    videos = []
    if video_ids:
        data = api_get("videos", {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
        })
        videos = data.get("items", [])

    videos.sort(
        key=lambda v: v.get("statistics", {}).get("viewCount", 0),
        reverse=True,
    )

    lines = [
        "# Daily Shorts — Channel Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Channel: {channel['snippet']['title']}",
        f"Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}",
        f"Total views: {channel['statistics'].get('viewCount', 'Unknown')}",
        f"Total videos: {channel['statistics'].get('videoCount', 'Unknown')}",
        "",
        "## Latest videos, ranked by views",
        "",
        "| Video | Views | Likes | Comments |",
        "|---|---:|---:|---:|",
    ]

    for video in videos:
        title = video["snippet"]["title"].replace("|", "-").replace("\n", " ")
        stats = video.get("statistics", {})
        video_id = video["id"]
        lines.append(
            f"| [{title}](https://youtube.com/watch?v={video_id}) "
            f"| {stats.get('viewCount', '—')} "
            f"| {stats.get('likeCount', 'Hidden')} "
            f"| {stats.get('commentCount', 'Hidden')} |"
        )

    lines += [
        "",
        "## Next steps",
        "",
        "- Review the best-performing videos for reusable topic ideas.",
        "- Compare view counts again in future reports to identify growth.",
        "- Review comments and prepare genuine replies.",
        "",
        "Note: this report covers the latest 10 uploads, not lifetime rankings.",
    ]

    with open("report.md", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print("Report generated successfully.")


if __name__ == "__main__":
    main()
