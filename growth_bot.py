
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]
BASE = "https://www.googleapis.com/youtube/v3"
HANDLE = "dailyshorts6363"
CHANNEL_URL = "https://youtube.com/@dailyshorts6363"


def youtube_get(endpoint, **params):
    params["key"] = API_KEY
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "TrinityGrowthBot/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    result = youtube_get(
        "channels",
        part="snippet,contentDetails",
        forHandle=HANDLE,
    )
    channels = result.get("items", [])
    if not channels:
        raise RuntimeError(f"Channel @{HANDLE} was not found.")

    channel = channels[0]
    uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist = youtube_get(
        "playlistItems",
        part="snippet,contentDetails",
        playlistId=uploads_id,
        maxResults=5,
    )

    videos = []
    for item in playlist.get("items", []):
        video_id = item["contentDetails"]["videoId"]
        title = item["snippet"]["title"].replace("\n", " ").strip()
        videos.append({
            "id": video_id,
            "title": title,
            "url": f"https://youtube.com/shorts/{video_id}",
        })

    lines = [
        "# Trinity — Daily Promotion Queue",
        "",
        f"Generated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}",
        "",
        f"Channel: {CHANNEL_URL}",
        "",
        "> Drafts only. Review platform rules and relevance before publishing.",
        "",
    ]

    for number, video in enumerate(videos, start=1):
        title = video["title"]
        url = video["url"]

        lines += [
            f"## {number}. {title}",
            "",
            f"**Video:** {url}",
            "",
            "### YouTube",
            "",
            f"Suggested CTA: Enjoyed {title}? Subscribe to Daily Shorts "
            "for more videos like this.",
            "",
            "### Reddit",
            "",
            f"Draft: I came across this short about {title}. "
            "What do you think?",
            "",
            "Only use this draft in a relevant community that permits "
            "sharing your own videos. Disclose that it is your video. "
            "Do not post it repeatedly or as an unsolicited comment.",
            "",
            "### TikTok / Instagram Reels",
            "",
            f"Caption idea: {title} — watch to the end! "
            "#shorts #dailyshorts",
            "",
            f"Source video: {url}",
            "",
            "---",
            "",
        ]

    if not videos:
        lines.append("No recent videos were returned by the YouTube API.")

    with open("promotion_queue.md", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print(f"Created promotion queue for {len(videos)} videos.")


if __name__ == "__main__":
    main()
