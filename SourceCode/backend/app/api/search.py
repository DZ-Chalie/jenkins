
from fastapi import APIRouter, HTTPException
from app.utils.es_client import get_es_client
from app.db.mariadb import get_liquor_details
from app.utils.search_stats import save_search_query, get_top_searches
from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str

router = APIRouter()

def search_liquor_fuzzy(text: str):
    es = get_es_client()
    if not es:
        print("❌ Elasticsearch client not available")
        return None

    # Search query: Match 'name' in 'liquor_integrated' index
    index_name = "liquor_integrated"
    
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "name": {
                                "query": text,
                                "fuzziness": "AUTO",
                                "boost": 1.0, 
                                "operator": "or"
                            }
                        }
                    },
                    {
                        "match": {
                            "name.ngram": { 
                                "query": text,
                                "fuzziness": "AUTO",
                                "boost": 10.0
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "min_score": 1.0, 
        "size": 10
    }

    try:
        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']
        
        if hits:
            best_match = hits[0]['_source']
            score = hits[0]['_score']
            
            print(f"✅ ES Match Found: '{best_match.get('name')}' (Score: {score})")
            
            # Transform ES data to Frontend 'SearchResult' interface
            source = best_match
            
            # Type mapping (approximate based on common IDs)
            type_map = {
                1: "과실주", 2: "리큐르/기타주류", 3: "약주,청주", 4: "증류주", 
                5: "탁주(고도0)", 6: "탁주(저도)", 7: "기타"
            }
            type_id = source.get('type_id')
            drink_type = type_map.get(type_id, "전통주") if type_id else "전통주"

            # Format ABV
            abv = source.get('drink_abv')
            if abv:
                try:
                    abv_float = float(abv)
                    if abv_float < 1.0:
                        abv = f"{int(abv_float * 100)}%"
                    else:
                        abv = f"{abv}%"
                except ValueError:
                    abv = f"{abv}%"

            result = {
                "id": source.get('drink_id'),
                "name": source.get('name'),
                "description": source.get('description') or source.get('intro'),
                "intro": source.get('intro'), 
                "image_url": source.get('image_url'),
                "url": source.get('url', ''),
                "tags": [], 
                "score": score,
                "detail": {
                    "알콜도수": f"{source.get('alcohol')}%",
                    "용량": source.get('volume'),
                    "종류": source.get('type'),
                    "원재료": source.get('ingredients'),
                    "수상내역": ", ".join(source.get('awards', [])) if isinstance(source.get('awards'), list) else str(source.get('awards', ''))
                },
                "brewery": {
                    "name": None, 
                    "address": source.get('region', {}).get('city'),
                    "homepage": None,
                    "contact": None
                },
                "pairing_food": source.get('foods', []), 
                "cocktails": source.get('cocktails', []), 
                "selling_shops": source.get('selling_shops', []), 
                "encyclopedia": source.get('description', ''), # Mapping description here too or separate?
                "candidates": [
                    {
                        "name": hit['_source']['name'],
                        "score": hit['_score'],
                        "image_url": hit['_source'].get('image_url', ''),
                        "id": hit['_source'].get('drink_id')
                    }
                    for hit in response['hits']['hits'][:5]
                ]
            }
            
            return result
        
        print(f"❌ No ES match found for '{text}'")
        return None

    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

class SearchRequest(BaseModel):
    query: str

@router.post("")
async def search_endpoint(request: SearchRequest):
    result = search_liquor_fuzzy(request.query)
    if not result:
        raise HTTPException(status_code=404, detail="Liquor not found")
    return result

# Weather-based recommendation weights
WEATHER_WEIGHTS = {
    "rain": {"탁주": 3, "탁주(고도0)": 3, "탁주(저도)": 3, "약주": 2, "약주,청주": 2},
    "snow": {"증류주": 3, "약주": 2, "약주,청주": 2},
    "cold": {"증류주": 3, "약주": 2, "약주,청주": 2},
    "hot": {"과실주": 3, "탁주": 2, "탁주(저도)": 2, "리큐르/기타주류": 2},
    "clear": {"약주": 2, "약주,청주": 2, "과실주": 2}
}

@router.get("/region")
async def search_by_region(
    province: str, 
    city: Optional[str] = None, 
    season: Optional[str] = None, 
    weather_condition: Optional[str] = None,
    weather_sort: bool = False,
    size: int = 1000
):
    """
    Search drinks by region using Elasticsearch for high performance.
    Supports filtering by season (Spring, Summer, Autumn, Winter).
    Supports weather-based sorting when weather_sort=true.
    """
    es = get_es_client()
    if not es:
        # Fallback to DB if ES is down (optional, but good for reliability)
        print("⚠️ ES unavailable, falling back to DB...")
        # ... (We could keep the DB logic here as fallback, but for now let's rely on ES as requested)
        raise HTTPException(status_code=500, detail="Search Engine Error")

    # Build ES Query
    # Note: 'province' and 'city' are nested in 'region' in ETL, but mapped flat?
    # Checked ETL: "region": { "province": ..., "city": ... }
    # So we need nested query or use dot notation if mapped as object?
    # Default dynamic mapping for dict is object. So 'region.province'.
    
    must_conditions = [
        {"match": {"region.province": province}}
    ]
    
    if city:
        must_conditions.append({"match": {"region.city": city}})

    if season:
        must_conditions.append({"match": {"season": season}})

    query = {
        "query": {
            "bool": {
                "must": must_conditions
            }
        },
        "sort": [
            {"lowest_price": {"order": "asc", "missing": "_last"}} 
        ],
        "size": size
    }
    
    try:
        response = es.search(index="liquor_integrated", body=query)
        hits = response['hits']['hits']
        
        results = []
        for hit in hits:
            source = hit['_source']
            name = source.get('name')
            
            results.append({
                "id": source.get('drink_id'),
                "name": name,
                "image_url": source.get('image_url'),
                "type": source.get('type') or "전통주",
                "alcohol": f"{source.get('alcohol')}%",
                "price": source.get('lowest_price', 0), # Direct from unified index
                "volume": source.get('volume'),
                "province": source.get('region', {}).get('province'),
                "city": source.get('region', {}).get('city')
            })
        
        # Apply weather-based sorting
        if weather_sort and weather_condition:
            weights = WEATHER_WEIGHTS.get(weather_condition, {})
            for item in results:
                type_name = item.get("type", "")
                item["weather_score"] = weights.get(type_name, 1)
            # Sort by weather_score descending, then by price ascending
            results.sort(key=lambda x: (-x.get("weather_score", 1), x.get("price", 999999)))
            
        return results

    except Exception as e:
        print(f"❌ ES Region Search Error: {e}")
        return []


@router.get("/detail/{drink_id}")
async def get_drink_detail(drink_id: int):
    """
    Get detailed information for a specific drink by ID.
    """
    es = get_es_client()
    if not es:
        raise HTTPException(status_code=500, detail="Search Engine Error")

    try:
        # Search by drink_id
        query = {
            "query": {
                "term": {
                    "drink_id": drink_id
                }
            }
        }
        
        response = es.search(index="liquor_integrated", body=query)
        hits = response['hits']['hits']
        
        if not hits:
            raise HTTPException(status_code=404, detail="Drink not found")
            
        source = hits[0]['_source']
        
        # 술 상세 정보 조회 통계 저장
        drink_name = source.get('name')
        drink_id_value = source.get('drink_id')
        if drink_name:
            await save_search_query(drink_name, drink_id=drink_id_value)
        
        return {
            "id": source.get('drink_id'),
            "name": source.get('name'),
            "description": source.get('description') or source.get('intro', ''),
            "intro": source.get('intro'),
            "image_url": source.get('image_url'),
            "abv": f"{source.get('alcohol')}%",
            "volume": source.get('volume'),
            "type": source.get('type'),
            "foods": source.get('foods', []),
            "cocktails": source.get('cocktails', []),
            "encyclopedia": source.get('encyclopedia', []), # Encyclopedia content (sections list)
            "selling_shops": source.get('selling_shops', []),
            "brewery": {
                "name": None,
                "address": source.get('region', {}).get('city'),
                 "homepage": None,
                "contact": None
            },
            "province": source.get('region', {}).get('province'),
            "city": source.get('region', {}).get('city'),
            "detail": {
                "알콜도수": f"{source.get('alcohol')}%",
                "용량": source.get('volume'),
                "종류": source.get('type'),
                "원재료": source.get('ingredients', ''),
                "수상내역": ", ".join(source.get('awards', [])) if isinstance(source.get('awards'), list) else str(source.get('awards', ''))
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Detail Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
class SimilarSearchRequest(BaseModel):
    name: str
    exclude_id: Optional[int] = None

def search_similar_drinks(name: str, exclude_id: Optional[int] = None):
    es = get_es_client()
    if not es:
        return []

    index_name = "drink_info"
    
    # Fuzzy search query
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "drink_name": {
                                "query": name,
                                "fuzziness": "AUTO",
                                "operator": "or" # Allow partial matches for similarity
                            }
                        }
                    }
                ],
                "must_not": []
            }
        },
        "size": 6 # Fetch a few to filter
    }
    
    if exclude_id is not None:
        query["query"]["bool"]["must_not"].append({
            "term": {"drink_id": exclude_id}
        })

    try:
        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']
        
        results = []
        for hit in hits:
            source = hit['_source']
            results.append({
                "id": source.get('drink_id'),
                "name": source.get('drink_name'),
                "image_url": source.get('drink_image_url'),
                "score": hit['_score']
            })
            
        return results

    except Exception as e:
        print(f"❌ Similar Search Error: {e}")
        return []

@router.post("/similar")
async def search_similar_endpoint(request: SimilarSearchRequest):
    return search_similar_drinks(request.name, request.exclude_id)

@router.get("/list")
async def get_drink_list(page: int = 1, size: int = 10, query: Optional[str] = None):
    """
    Get paginated list of all drinks from Elasticsearch.
    Supports optional search query.
    """
    es = get_es_client()
    if not es:
        raise HTTPException(status_code=500, detail="Search Engine Error")

    try:
        # Calculate pagination
        from_index = (page - 1) * size
        
        # Build query
        if query:
            es_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "intro", "description"],
                        "fuzziness": "AUTO"
                    }
                },
                "from": from_index,
                "size": size,
                "sort": [{"drink_id": {"order": "asc"}}]
            }
        else:
            es_query = {
                "query": {"match_all": {}},
                "from": from_index,
                "size": size,
                "sort": [{"drink_id": {"order": "asc"}}]
            }
        
        response = es.search(index="liquor_integrated", body=es_query)
        hits = response['hits']['hits']
        total = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
        
        results = []
        for hit in hits:
            source = hit['_source']
            
            results.append({
                "id": source.get('drink_id'),
                "name": source.get('name'),
                "image_url": source.get('image_url'),
                "type": source.get('type') or "전통주",
                "alcohol": f"{source.get('alcohol')}%",
                "volume": source.get('volume'),
                "price": source.get('lowest_price', 0),
                "intro": source.get('intro', '') or source.get('description', ''),
                "pairing_foods": source.get('foods', []),
                "selling_shops": source.get('selling_shops', [])
            })
        
        return {
            "drinks": results,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }

    except Exception as e:
        print(f"❌ List Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-searches")
async def get_top_searches_endpoint(limit: int = 10):
    """오늘 하루 동안 가장 많이 검색된 검색어 Top N 반환"""
    results = await get_top_searches(limit)
    return {"top_searches": results}

@router.get("/products/{drink_name}")
async def get_products_by_drink(drink_name: str):
    """
    특정 술의 판매 상품 목록 조회 (products_liquor 인덱스)
    
    Args:
        drink_name: 술 이름
        
    Returns:
        가격순 정렬된 판매 상품 목록
    """
    es = get_es_client()
    if not es:
        return {"drink_name": drink_name, "products": [], "count": 0}
    
    try:
        query = {
            "query": {
                "term": {
                    "drink_name.keyword": drink_name
                }
            },
            "sort": [
                {"lprice": {"order": "asc"}}
            ],
            "size": 10  # 최대 10개 판매처
        }
        
        response = es.search(index="products_liquor", body=query)
        
        products = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            products.append({
                "name": source.get('name', ''),
                "price": source.get('lprice', 0),
                "shop": source.get('mall_name', ''),
                "url": source.get('link', ''),
                "image_url": source.get('image', '')
            })
        
        return {
            "drink_name": drink_name,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        print(f"❌ Error fetching products for {drink_name}: {e}")
        return {"drink_name": drink_name, "products": [], "count": 0}

