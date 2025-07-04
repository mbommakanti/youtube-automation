import sys
from pathlib import Path
import logging
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from config import Config

import os
import json
import isodate
from ratelimit import limits, sleep_and_retry

import requests

def setup_logging():
    """Configure logging based on configuration settings"""
    config = Config.get_instance()
    
    # Create log folder if needed (local environment)
    if config.should_create_log_folder and config.log_file_path:
        from pathlib import Path
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get handlers based on configuration
    handlers = []
    
    if config.log_handler == 'file' and config.log_file_path:
        # File handler for local development
        handlers.append(logging.FileHandler(config.log_file_path, encoding='utf-8'))
    
    if config.log_handler == 'console' or config.environment == 'production':
        # Console handler (always include for production/Lambda)
        handlers.append(logging.StreamHandler())
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )

setup_logging()
logger = logging.getLogger(__name__)

def load_api_key():
    """Helper method to load API Key from the config file"""
    config = Config.get_instance()
    youTubeAPIKey = config.config.youtube.apiKey
    return youTubeAPIKey

@sleep_and_retry
@limits(calls=5,period=60)
def make_API_Call(url, params, methodType="GET"):
    """Helper method to make an API call and return a structured response"""
    try:
        if methodType.upper() == "POST":
            logger.debug(f"Params being passed are: {params}")
            response = requests.post(url, data=params,timeout=5)
        else:
            logger.debug(f"Params being passed are: {params}")
            response = requests.get(url, params=params,timeout=5)
        response.raise_for_status()  # raises HTTPError for bad responses (4xx or 5xx)
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.Timeout:
        logger.warning(f" Request timed out for {url}")
        return {
            "success": False,
            "error": "Request timeout",       # include error detail for debugging
            "data": None
        }

    except requests.exceptions.RequestException as e:
        logger.error(f" API Call failed: {e}")
        return {
            "success": False,
            "error": str(e),       # include error detail for debugging
            "data": None
        }

def videoItemParser(item):
    currentVideoDetails = {}
    durationOfTheVideo = item.get("contentDetails",{}).get("duration","") 
    try:
        parsedDuration = isodate.parse_duration(durationOfTheVideo)
        durationInSeconds = parsedDuration.total_seconds()
    except (TypeError, isodate.ISO8601Error):
        durationInSeconds = 0.0
        return currentVideoDetails
    if durationInSeconds < 60 and durationInSeconds > 5:
        currentVideoDetails["id"] = item.get("id","") 
        currentVideoDetails["publishedAt"] = item.get("snippet",{}).get("publishedAt","") 
        currentVideoDetails["channelId"] = item.get("snippet",{}).get("channelId","") 
        currentVideoDetails["title"] = item.get("snippet",{}).get("title","") 
        currentVideoDetails["channelTitle"]=item.get("snippet",{}).get("channelTitle","") 
        currentVideoDetails["description"]=item.get("snippet",{}).get("description","") 
        currentVideoDetails["tags"]=item.get("snippet",{}).get("tags","") 
        currentVideoDetails["durationInSeconds"] = durationInSeconds
        currentVideoDetails["dimension"]=item.get("contentDetails",{}).get("dimension","") 
        currentVideoDetails["definition"]=item.get("contentDetails",{}).get("definition","") 
        currentVideoDetails["caption"]=item.get("contentDetails",{}).get("caption","") 
        currentVideoDetails["licensedContent"]=item.get("contentDetails",{}).get("licensedContent","") 
        currentVideoDetails["viewCount"]=item.get("statistics",{}).get("viewCount","") 
        currentVideoDetails["likeCount"]=item.get("statistics",{}).get("likeCount","") 
        currentVideoDetails["favoriteCount"]=item.get("statistics",{}).get("favoriteCount","") 
        currentVideoDetails["commentCount"]=item.get("statistics",{}).get("commentCount","") 

    return currentVideoDetails
    
def fetch_most_popular_videos(region_configs,target_per_region=50):
    """Main method to fetch the youtube shorts based on the region configuration"""
    final_results={}
    api_key = load_api_key()
    for region_config in region_configs:
        logger.info(f"Beginning Processing the Region {region_config}")
        collected_videos=[]
        pageToken = None
        processedVideos = 0

        while(len(collected_videos)<target_per_region and processedVideos<500):
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_config.get('region'),
                'relevanceLanguage': region_config.get('language'),
                'maxResults': 50,
                'pageToken': pageToken,
                'key':api_key
             }
            apiResponse = make_API_Call('https://www.googleapis.com/youtube/v3/videos',params,"get")
            if(apiResponse["success"]):
                responseData = apiResponse["data"]
                if responseData.get('items'):
                    for item in responseData.get('items'):
                        if any(item.get("id")==existingItems["id"] for existingItems in collected_videos):
                            processedVideos+=1
                        else:
                            processedVideos+=1
                            processedVideoItem = videoItemParser(item)
                            if processedVideoItem:
                                collected_videos.append(processedVideoItem)
                if(responseData.get("nextPageToken")):
                    pageToken = responseData.get("nextPageToken")
                else:
                    break
            else:
                break

        
        key = f"{region_config['region']}_{region_config['language']}"
        if len(collected_videos)>0:
            final_results[key] = collected_videos 
            logger.info(f"Ending Processing the Region {region_config}")
    return final_results
            

if __name__=="__main__":
    region_configs = [{"region":"IN","language":"te"},{"region":"IN","language":"hi"}]
    videos = fetch_most_popular_videos(region_configs,2)
    logger.info("Final Videos are:\n%s", videos)



