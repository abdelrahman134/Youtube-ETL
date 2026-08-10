from dotenv import load_dotenv
import requests
import os
import json
load_dotenv('.env')

API_KEY = os.getenv('API_KEY')


def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle=MrBeast&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        channel=data["items"][0]
        playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        return playlist_id
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def get_video_ids(playlist_id):
    max_results = 50
    playlist_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}"
    video_ids = []
    page_token = None
    try:
        while True:
            url=playlist_url
            if page_token:
                url += f"&pageToken={page_token}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            video_id = [item["contentDetails"]["videoId"] for item in data["items"]]
            video_ids.extend(video_id)

            if "nextPageToken" in data:
                page_token = data["nextPageToken"]
            else:
                break
        return video_ids
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def extract_video_data(video_ids):
    def batch_list(video_lst, batch_size):
        for i in range(0, len(video_lst), batch_size):
            yield video_lst[i:i + batch_size]
            
    # 1. Initialize the list OUTSIDE the loop so it collects all batches
    selected_data = []
    
    for batch in batch_list(video_ids, 50):
        video_ids_str = ",".join(batch)
        
        # 2. Fix the typo "snippets" -> "snippet" and combine them with commas
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails,snippet,statistics&id={video_ids_str}&key={API_KEY}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  
            data = response.json()
            
            for item in data.get("items", []):
                print(f"Video ID: {item['id']}, Title: {item['snippet']['title']}, Views: {item['statistics'].get('viewCount', 0)}")
                selected_data.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "duration": item["contentDetails"]["duration"], 
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": item["statistics"].get("viewCount", 0),
                    "like_count": item["statistics"].get("likeCount", 0),
                    "comment_count": item["statistics"].get("commentCount", 0)
                })
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            
    # 3. Return the fully populated list OUTSIDE the loop
    return selected_data    

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    print(extract_video_data(video_ids))