import os  
import time  
import requests  
from dotenv import load_dotenv, set_key  
  
# 1st step: load the env once  
load_dotenv()  
  
def get_valid_token():  
    """Returns a valid access token, refreshing it if necessary."""  
    expires_at = int(os.getenv("STRAVA_EXPIRES_AT"))  
      
    # checlking if current time is past the expiration (with a 60s buffer)  
    if time.time() > (expires_at - 60):  
        print("Token expired or expiring soon. Refreshing...")  
          
        response = requests.post(  
            "https://www.strava.com/api/v3/oauth/token",  
            data={  
                "client_id": os.getenv("STRAVA_CLIENT_ID"),  
                "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),  
                "grant_type": "refresh_token",  
                "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN"),  
            }  
        ).json()  
  
        # Update the .env file so the NEXT run sees the new values  
        set_key(".env", "STRAVA_ACCESS_TOKEN", response["access_token"])  
        set_key(".env", "STRAVA_EXPIRES_AT", str(response["expires_at"]))  
        set_key(".env", "STRAVA_REFRESH_TOKEN", response["refresh_token"])  
          
        # Update the current session's environment variables  
        os.environ["STRAVA_ACCESS_TOKEN"] = response["access_token"]  
        os.environ["STRAVA_EXPIRES_AT"] = str(response["expires_at"])  
        os.environ["STRAVA_REFRESH_TOKEN"] = response["refresh_token"]  
  
        return response["access_token"]  
      
    return os.getenv("STRAVA_ACCESS_TOKEN")  

