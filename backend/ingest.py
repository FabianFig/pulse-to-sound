import os
import json
import requests
from auth import get_valid_token  # Using your gatekeeper function

RAW_DIR = "data/raw/activities"
STREAMS_DIR = "data/raw/streams"

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(STREAMS_DIR, exist_ok=True)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def fetch_all_data():
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch the summary list (Layer 1)
    res = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params={"per_page": 200})
    activities = res.json()
    
    for activity in activities:
        activity_id = activity['id']
        print(f"Processing Activity: {activity_id}")
        
        # Save the summary obj
        save_json(activity, f"{RAW_DIR}/{activity_id}.json")
        
        # 2. Fetch streams (Layer 1)
        # request common keys for your generative sound (Layer 6)
        stream_url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
        stream_params = {"keys": "time,distance,latlng,altitude,velocity_smooth,heartrate,watts", "key_by_type": True}
        
        s_res = requests.get(stream_url, headers=headers, params=stream_params)
        if s_res.status_code == 200:
            save_json(s_res.json(), f"{STREAMS_DIR}/{activity_id}_streams.json")

if __name__ == "__main__":
    fetch_all_data()