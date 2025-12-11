# 검색어 통계를 저장하는 함수
from datetime import datetime, timedelta
from app.db.mongodb import get_database

async def save_search_query(query: str, drink_id: int = None):
    """검색어를 MongoDB에 저장 (술 이름과 drink_id 함께 저장)"""
    try:
        db = await get_database()
        collection = db.search_logs
        
        # 오늘 날짜의 시작 (00:00:00)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 검색어를 정규화 (공백 제거)
        normalized_query = query.strip()
        
        # 검색어와 drink_id로 고유 키 생성 (같은 술의 조회는 하나로 집계)
        filter_query = {
            "query": normalized_query,
            "date": today
        }
        
        # drink_id가 있으면 필터에 추가
        if drink_id:
            filter_query["drink_id"] = drink_id
        
        update_data = {
            "$inc": {"count": 1},
            "$setOnInsert": {"created_at": datetime.now()}
        }
        
        # drink_id가 있으면 저장
        if drink_id:
            update_data["$setOnInsert"]["drink_id"] = drink_id
        
        # 오늘 날짜에 해당 검색어가 있으면 count 증가, 없으면 생성
        await collection.update_one(
            filter_query,
            update_data,
            upsert=True
        )
        
        print(f"✅ Search query saved: {normalized_query} (drink_id: {drink_id})")
    except Exception as e:
        print(f"❌ Error saving search query: {e}")

async def get_top_searches(limit: int = 10):
    """오늘 하루 동안 가장 많이 검색된 검색어 Top N 반환 (drink_id 포함)"""
    try:
        db = await get_database()
        collection = db.search_logs
        
        # 오늘 날짜의 시작
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 오늘 날짜의 검색어를 count 내림차순으로 정렬
        cursor = collection.find(
            {"date": today, "drink_id": {"$exists": True}}  # drink_id가 있는 것만
        ).sort("count", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            results.append({
                "query": doc.get("query", ""),
                "count": doc.get("count", 0),
                "drink_id": doc.get("drink_id")
            })
        
        return results
    except Exception as e:
        print(f"❌ Error getting top searches: {e}")
        return []
