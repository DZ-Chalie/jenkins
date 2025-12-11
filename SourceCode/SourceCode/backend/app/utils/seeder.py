from app.utils.es_client import get_es_client, create_index_if_not_exists

SAMPLE_DATA = [
    {
        "name": "느린마을 막걸리",
        "description": "인공 감미료 없이 쌀, 누룩, 물로만 빚은 프리미엄 막걸리. 시간이 지날수록 맛이 변화하는 것이 특징.",
        "tags": ["막걸리", "달콤함", "부드러움", "무감미료"]
    },
    {
        "name": "복순도가 손막걸리",
        "description": "천연 탄산이 가득하여 샴페인 같은 청량감을 주는 막걸리. 새콤달콤한 맛이 일품.",
        "tags": ["막걸리", "탄산", "새콤달콤", "스파클링"]
    },
    {
        "name": "화요 25",
        "description": "우리 쌀 100%와 지하 150m 암반수로 빚은 증류식 소주. 깔끔하고 부드러운 목넘김.",
        "tags": ["소주", "증류식", "깔끔함", "25도"]
    },
    {
        "name": "서울의 밤",
        "description": "황매실을 증류하여 만든 리큐르. 매실의 향긋함과 깔끔한 맛이 조화로움.",
        "tags": ["리큐르", "매실", "서울", "향긋함"]
    },
    {
        "name": "참이슬",
        "description": "대한민국 대표 희석식 소주. 깨끗하고 깔끔한 맛.",
        "tags": ["소주", "희석식", "국민술"]
    }
]

def seed_data():
    es = get_es_client()
    if not es:
        return

    create_index_if_not_exists(es)

    for liquor in SAMPLE_DATA:
        # Use name as ID to prevent duplicates
        es.index(index="liquors", id=liquor["name"], document=liquor)
        print(f"Indexed: {liquor['name']}")

if __name__ == "__main__":
    seed_data()
