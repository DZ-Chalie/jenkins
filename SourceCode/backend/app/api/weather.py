from fastapi import APIRouter, HTTPException, Query
from app.utils.weather import get_weather_by_adm_cd, get_weather_by_city, is_city_level_name, MOCK_WEATHER_DATA, get_code_from_city
from app.api.search import search_liquor_fuzzy
import random

from collections import Counter

router = APIRouter()

@router.get("/recommend")
async def recommend_by_weather(
    adm_cd: str = Query(..., description="시/도 코드 (예: 11=서울, 41=경기)"),
    city: str = Query(None, description="시/군/구 이름 (예: 수원시, 가평군)")
):
    """
    날씨 기반 전통주 추천 API
    """
    # 1. 날씨 정보 조회
    # NO CITY SELECTED: Return aggregate province weather + available cities
    # NO CITY SELECTED: Return available cities only
    if not city:
        # Fetch province data (contains 1 real + N dummies)
        items = await get_weather_by_adm_cd(adm_cd)
        
        available_cities = []
        
        for item in items:
            name = item.get("SGG_NM") or item.get("ADM_NM") or item.get("ADM_NM2")
            if name and is_city_level_name(name):
                if name not in available_cities:
                    available_cities.append(name)
        
        available_cities.sort()
        
        return {
            "city": "", 
            "temperature": None,
            "weather": None,
            "message": "상세 날씨를 보려면 시/군을 선택해주세요.",
            "keyword": "",
            "liquors": [],
            "available_cities": available_cities
        }
    
    # CITY SELECTED: Fetch specific city weather using hybrid cache
    target_weather = await get_weather_by_city(adm_cd, city)
    
    # Also fetch full province data for available_cities
    items = await get_weather_by_adm_cd(adm_cd)
    
    # 2. Extract available cities
    available_cities = []
    for item in items:
        name = item.get("SGG_NM") or item.get("ADM_NM") or item.get("ADM_NM2")
        if name and is_city_level_name(name) and name not in available_cities:
            available_cities.append(name)
    
    available_cities.sort()
    
    # 3. Validate target_weather
    if not target_weather:
        return {
            "city": city,
            "temperature": None,
            "weather": "Unknown",
            "message": f"{city}의 날씨 정보를 찾을 수 없습니다.",
            "keyword": "",
            "liquors": [],
            "available_cities": available_cities
        }

    # 날씨 데이터 파싱
    try:
        temp = float(target_weather.get("NOW_AIRTP", 0))    # 기온
        sky_code = target_weather.get("SKY_STTS", "1")      # 하늘 상태 (1:맑음, 3:구름많음, 4:흐림)
        rain_type = target_weather.get("PCPTTN_SHP", "0")   # 강수 형태 (0:없음, 1:비, 2:비/눈, 3:눈, 4:소나기)
    except:
        temp = 20
        sky_code = "1"
        rain_type = "0"

    weather_desc = "맑음"
    search_keyword = "전통주"
    recommendation_msg = "오늘 같은 날엔 우리술 한 잔 어떠세요?"

    # 3. 날씨별 추천 로직
    # 강수 형태: 0(없음), 1(비), 2(비/눈), 3(눈), 4(소나기), 5(빗방울), 6(빗방울눈날림), 7(눈날림)
    if rain_type in ["1", "4", "5"]:  # 비, 소나기, 빗방울
        weather_desc = "비"
        search_keyword = "막걸리"
        recommendation_msg = f"{city}에는 비가 내리고 있어요.\n비 오는 날엔 역시 파전에 막걸리죠!"
    elif rain_type in ["2", "6"]:  # 비/눈, 빗방울눈날림
        weather_desc = "진눈깨비"
        search_keyword = "증류주"
        recommendation_msg = f"{city}에는 진눈깨비가 내리네요.\n쌀쌀한 날씨에 따뜻한 증류주 한 잔 어떠세요?"
    elif rain_type in ["3", "7"]:  # 눈, 눈날림
         weather_desc = "눈"
         search_keyword = "도수 높은"
         recommendation_msg = f"{city}에는 눈이 오네요.\n추위를 녹여줄 따뜻하고 도수 높은 술은 어떠세요?"
    else:
        # 비/눈이 안 올 때 기온 기준
        if temp >= 28:
            weather_desc = "무더움"
            search_keyword = "과실주"
            recommendation_msg = f"오늘 {city} 날씨가 참 덥죠?\n갈증을 해소해줄 시원하고 상큼한 과실주 어떠세요?"
        elif temp <= 5:
            weather_desc = "추움"
            search_keyword = "증류주"
            recommendation_msg = f"쌀쌀한 {city} 날씨엔,\n몸을 데워줄 깊은 풍미의 증류주가 딱이에요."
        elif sky_code in ["3", "4"]:
            weather_desc = "흐림"
            search_keyword = "약주"
            recommendation_msg = f"{city} 하늘이 흐리네요.\n운치 있는 날씨에 깔끔한 약주 한 잔 어떠세요?"
        else:
            weather_desc = "맑음"
            search_keyword = "청주"
            recommendation_msg = f"화창한 {city} 날씨!\n맑은 날씨만큼 깨끗한 청주와 함께 즐겨보세요."

    # 4. 술 검색 수행 (Search API 재사용)
    # search_liquor_fuzzy를 사용하여 키워드로 검색
    search_result = search_liquor_fuzzy(search_keyword)
    
    # fuzzy search returns a SINGLE result dict usually, or None. 
    # But search_liquor_fuzzy logic inside actually searches size=10 but returns ONE best match transformed.
    # We might want a LIST. `search.py` has `get_drink_list` but that's pagination.
    # Does `search_liquor_fuzzy` return specific type? It mostly targets finding A drink by name.
    
    # Better approach: We want a list of recommendations. 
    # Let's use ES directly here to get a LIST, or modify search logic to return list.
    # For now, to suffice the "recommendation", finding ONE best representative or a few is good.
    # But `search_liquor_fuzzy` returns just one detailed result.
    
    # Alternative: Use `search_similar_drinks` if we had a seed drink.
    # Alternative 2: Use `es.search` directly here to get multiple items for the keyword.
    
    from app.utils.es_client import get_es_client
    es = get_es_client()
    liquors = []
    
    if es:
        query = {
            "query": {
                "match": {
                    "drink_name": search_keyword # Search by our keyword
                }
            },
            "size": 5
        }
        try:
             res = es.search(index="drink_info", body=query)
             for hit in res['hits']['hits']:
                 src = hit['_source']
                 liquors.append({
                     "id": src.get('drink_id'),
                     "name": src.get('drink_name'),
                     "image_url": src.get('drink_image_url'),
                     "type": search_keyword, # approximating logic
                     "score": hit['_score']
                 })
        except Exception as e:
            print(f"Weather Recommendation Search Error: {e}")

    return {
        "city": city,
        "temperature": temp,
        "weather": weather_desc,
        "message": recommendation_msg,
        "keyword": search_keyword,
        "message": recommendation_msg,
        "keyword": search_keyword,
        "liquors": liquors,
        "available_cities": available_cities
    }
