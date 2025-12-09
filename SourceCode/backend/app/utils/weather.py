import requests
import asyncio
import os
import urllib3
import json
import redis
import logging
from typing import List, Dict, Any
from urllib.parse import unquote
import random
from datetime import datetime

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis Connection
try:
    redis_client = redis.StrictRedis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD", None),
        decode_responses=True,
        socket_timeout=2
    )
    redis_client.ping()
    logger.info("✅ Connected to Redis")
except Exception as e:
    logger.error(f"❌ Redis Connection Failed: {e}")
    redis_client = None

# SSL Warning Disable
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Mock Data for Fallback (Compatibility)
MOCK_WEATHER_DATA = {
    "11": [{"SGG_NM": "종로구", "NOW_AIRTP": "20", "PCPTTN_SHP": "0", "SKY_STTS": "1"}],
    "26": [{"SGG_NM": "해운대구", "NOW_AIRTP": "20", "PCPTTN_SHP": "0", "SKY_STTS": "1"}],
    "41": [{"SGG_NM": "수원시", "NOW_AIRTP": "20", "PCPTTN_SHP": "0", "SKY_STTS": "1"}],
    "42": [{"SGG_NM": "춘천시", "NOW_AIRTP": "20", "PCPTTN_SHP": "0", "SKY_STTS": "1"}]
}

# OpenWeatherMap Settings
OWM_API_KEY = os.getenv("OWM_API_KEY") # OWM Key
OWM_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Province Code to Representative City Mapping (English for OWM API)
PROVINCE_MAP = {
    "11": "Seoul",      # Seoul
    "26": "Busan",      # Busan
    "27": "Daegu",      # Daegu
    "28": "Incheon",    # Incheon
    "29": "Gwangju",    # Gwangju
    "30": "Daejeon",    # Daejeon
    "31": "Ulsan",      # Ulsan
    "36": "Sejong",     # Sejong
    "41": "Suwon",      # Gyeonggi-do
    "42": "Chuncheon",  # Gangwon-do
    "43": "Cheongju",   # Chungbuk
    "44": "Hongseong",  # Chungnam
    "45": "Jeonju",     # Jeonbuk
    "46": "Muan",       # Jeonnam
    "47": "Andong",     # Gyeongbuk
    "48": "Changwon",   # Gyeongnam
    "50": "Jeju",       # Jeju
}

# Province Code to Representative City Mapping (Korean for Display)
PROVINCE_REP_CITY_KR = {
    "11": "서울",
    "26": "부산",
    "27": "대구",
    "28": "인천",
    "29": "광주",
    "30": "대전",
    "31": "울산",
    "36": "세종",
    "41": "수원시",
    "42": "춘천시",
    "43": "청주시",
    "44": "홍성군",
    "45": "전주시",
    "46": "무안군",
    "47": "안동시",
    "48": "창원시",
    "50": "제주시"
}

def fetch_weather_sync(url: str, params: dict):
    """Sync wrapper for requests"""
    try:
        return requests.get(url, params=params, verify=False, timeout=10)
    except Exception as e:
        print(f"Requests Error: {e}")
        return None

async def fetch_owm_data(city_name: str):
    """Fetch weather data from OpenWeatherMap"""
    try:
        params = {
            "q": f"{city_name},KR",
            "appid": OWM_API_KEY,
            "units": "metric",
            "lang": "kr"
        }
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, fetch_weather_sync, OWM_BASE_URL, params)
        
        if response and response.status_code == 200:
            return response.json()
        else:
            logger.error(f"OWM API Error for {city_name}: {response.status_code if response else 'None'}")
            return None
    except Exception as e:
        logger.error(f"OWM Exception for {city_name}: {e}")
        return None

def map_owm_to_internal(owm_data: dict, city_name_kr: str) -> Dict[str, Any]:
    """
    Maps OWM response to the internal format expected by api/weather.py
    
    Internal Keys:
    - SGG_NM: City Name
    - NOW_AIRTP: Temperature (float string)
    - PCPTTN_SHP: Precip Type (0:None, 1:Rain, 2:Rain/Snow, 3:Snow, 4:Shower)
    - SKY_STTS: Sky State (1:Clear, 3:Cloudy, 4:Overcast)
    """
    if not owm_data:
        return {}

    temp = owm_data.get("main", {}).get("temp", 0)
    weather_id = owm_data.get("weather", [{}])[0].get("id", 800)
    
    # Map Precip Type
    # 2xx: Thunderstorm -> Rain(1) or Shower(4)? Let's say Rain(1)
    # 3xx: Drizzle -> Rain(1)
    # 5xx: Rain -> Rain(1)
    # 6xx: Snow -> Snow(3)
    # 611-616: Sleet -> Rain/Snow(2)
    
    rain_type = "0"
    if 200 <= weather_id < 600:
        rain_type = "1" # Rain
    elif 611 <= weather_id <= 616:
        rain_type = "2" # Sleet
    elif 600 <= weather_id < 700:
        rain_type = "3" # Snow
        
    # Map Sky State (only valid if rain_type is 0 usually, but we set it anyway)
    # 800: Clear -> 1
    # 801-802: Clouds -> 3
    # 803-804: Clouds -> 4
    
    sky_code = "1"
    if weather_id == 800:
        sky_code = "1"
    elif weather_id in [801, 802]:
        sky_code = "3"
    elif weather_id >= 803:
        sky_code = "4"
    elif 700 <= weather_id < 800: # Mist, Fog etc
        sky_code = "4"

    return {
        "SGG_NM": city_name_kr,
        "NOW_AIRTP": str(temp),
        "PCPTTN_SHP": rain_type,
        "SKY_STTS": sky_code
    }

async def get_weather_by_city(adm_cd: str, city_name: str) -> Dict[str, Any]:
    """
    Fetches weather for a specific city using OWM.
    Args:
        adm_cd: Province code (ignored for OWM query, used for cache key)
        city_name: Korean city name (e.g. "수원시", "가평군")
    """
    # 1. Check Cache
    if redis_client:
        try:
            cache_key = f"weather:owm:{adm_cd}:{city_name}"
            cached = redis_client.get(cache_key)
            if cached:
                # Extend current TTL by 10 minutes on cache hit (sliding window)
                current_ttl = redis_client.ttl(cache_key)
                if current_ttl > 0:
                    redis_client.expire(cache_key, current_ttl + 600)
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis Read Error: {e}")

    # 2. Fetch from OWM
    # Need to translate KR city name to Romanized for better OWM accuracy?
    # OWM supports local names but "Suwon-si" is safer than "수원시" sometimes.
    # However, user snippet used "Bucheon,KR".
    # Let's try to remove "시" or "군" for English query if needed, OR use google translate?
    # Actually OWM supports Korean query `q=수원시,KR`. Let's use that.
    
    owm_data = await fetch_owm_data(city_name)
    
    if owm_data:
        result = map_owm_to_internal(owm_data, city_name)
        
        # Cache
        if redis_client:
             try:
                cache_key = f"weather:owm:{adm_cd}:{city_name}"
                redis_client.setex(cache_key, 7200, json.dumps(result)) # 2 hour cache
             except Exception as e:
                logger.error(f"Redis Write Error: {e}")
        return result
    
    return {}

# Static list of cities per province for dropdown
PROVINCE_CITY_LIST = {
    "11": ["종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구", "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"],
    "26": ["중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구", "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"],
    "27": ["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군", "군위군"],
    "28": ["중구", "동구", "미추홀구", "연수구", "남동구", "부평구", "계양구", "서구", "강화군", "옹진군"],
    "29": ["동구", "서구", "남구", "북구", "광산구"],
    "30": ["동구", "중구", "서구", "유성구", "대덕구"],
    "31": ["중구", "남구", "동구", "북구", "울주군"],
    "36": ["세종시"],
    "41": ["수원시", "성남시", "의정부시", "안양시", "부천시", "광명시", "평택시", "동두천시", "안산시", "고양시", "과천시", "구리시", "남양주시", "오산시", "시흥시", "군포시", "의왕시", "하남시", "용인시", "파주시", "이천시", "안성시", "김포시", "화성시", "광주시", "양주시", "포천시", "여주시", "연천군", "가평군", "양평군"],
    "42": ["춘천시", "원주시", "강릉시", "동해시", "태백시", "속초시", "삼척시", "홍천군", "횡성군", "영월군", "평창군", "정선군", "철원군", "화천군", "양구군", "인제군", "고성군", "양양군"],
    "43": ["청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "증평군", "진천군", "괴산군", "음성군", "단양군"],
    "44": ["천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시", "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"],
    "45": ["전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", "완주군", "진안군", "무주군", "장수군", "임실군", "순창군", "고창군", "부안군"],
    "46": ["목포시", "여수시", "순천시", "나주시", "광양시", "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", "영암군", "무안군", "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"],
    "47": ["포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시", "군위군", "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군", "울진군", "울릉군"],
    "48": ["창원시", "진주시", "통영시", "사천시", "김해시", "밀양시", "거제시", "양산시", "의령군", "함안군", "창녕군", "고성군", "남해군", "하동군", "산청군", "함양군", "거창군", "합천군"],
    "50": ["제주시", "서귀포시"]
}

async def get_weather_by_adm_cd(adm_cd: str) -> List[Dict[str, Any]]:
    """
    Fetches representative weather for province using OWM map.
    Returns a list containing ONE representative item with weather, 
    PLUS dummy items for other cities to populate the dropdown.
    """
    if redis_client:
        try:
            cache_key = f"weather:owm:{adm_cd}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis Read Error: {e}")

    # Get representative city
    city_en = PROVINCE_MAP.get(adm_cd, "Seoul")
    
    owm_data = await fetch_owm_data(city_en)
    
    items = []
    if owm_data:
        # 1. Representative Item (with weather data)
        # Use Korean name for display
        rep_city_kr = PROVINCE_REP_CITY_KR.get(adm_cd, city_en)
        rep_item = map_owm_to_internal(owm_data, rep_city_kr)
        items.append(rep_item)
        
        # 2. Add Dummy items for city list
        # api/weather.py iterates items and checks SGG_NM to build `available_cities`.
        # We need to provide these items.
        city_list = PROVINCE_CITY_LIST.get(adm_cd, [])
        for city_ko in city_list:
            # Check if this city is the representative one we just added?
            # It's okay to have duplicates or we can just add them.
            # We add them with EMPTY weather data so they don't affect average much?
            # Or api/weather.py crashes if data missing?
            # api/weather.py: `try: float(item.get("NOW_AIRTP", 0)) ... except: pass`
            # So missing data is skipped for average but name is added to list.
            items.append({
                "SGG_NM": city_ko,
                # No weather info
            })
        
        if redis_client:
            redis_client.setex(f"weather:owm:{adm_cd}", 7200, json.dumps(items))
            
    return items

def get_code_from_city(city_name: str) -> str:
    """Legacy helper, kept for compatibility"""
    return "00000"

def is_city_level_name(name: str) -> bool:
    """Helper"""
    if not isinstance(name, str): return False
    return True # simplified

