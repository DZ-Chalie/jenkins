from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import boto3
from app.utils.es_client import get_es_client

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    drinks: List[dict]

def search_liquor_for_rag(text: str):
    es = get_es_client()
    if not es:
        print("❌ Elasticsearch client not available")
        return []

    index_name = "drink_info"
    
    # RAG용 검색 쿼리: 설명이나 소개글에서도 검색하여 문맥에 맞는 술을 찾음
    query = {
        "query": {
            "bool": {
                "should": [
                    { "match": { "drink_name": { "query": text, "boost": 3.0 } } },
                    { "match": { "drink_intro": { "query": text, "boost": 1.5 } } },
                    { "match": { "drink_desc": { "query": text, "boost": 1.0 } } },
                    { "match": { "pairing_foods": { "query": text, "boost": 2.0 } } }, # 안주로 검색 가능하게
                    { "match": { "drink_tag": { "query": text, "boost": 1.5 } } }
                ],
                "minimum_should_match": 1
            }
        },
        "min_score": 5.0, # 점수 임계값 상향 (엄격한 검색)
        "size": 5
    }

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
                "description": source.get('drink_intro') or source.get('drink_desc', '')[:100],
                "abv": source.get('drink_abv'),
                "volume": source.get('drink_volume'),
                "foods": source.get('pairing_foods', []),
                "full_desc": source.get('drink_desc', '')
            })
        return results
    except Exception as e:
        print(f"❌ ES Search error: {e}")
        return []

def invoke_nova(system_prompt: str, user_message: str):
    try:
        # AWS Bedrock Client
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        bedrock = session.client(service_name='bedrock-runtime')

        model_id = "amazon.nova-lite-v1:0"
        
        # Nova 모델 요청 바디 구성
        body = {
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }

        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                guardrailIdentifier="6lsrxzd5pnlq", 
                guardrailVersion="DRAFT" 
            )
        except Exception as e:
            # 가드레일에 걸리면 예외가 발생할 수 있음 (또는 응답에 포함)
            print(f"⚠️ Guardrail or Bedrock Error: {e}")
            return "그 이야기는 내 잘 모르겠고, 술 이야기나 합시다! 허허."

        response_body = json.loads(response.get('body').read())
        
        # Token Usage Logging
        usage = response_body.get('usage', {})
        input_tokens = usage.get('inputTokens', 0)
        output_tokens = usage.get('outputTokens', 0)
        total_tokens = usage.get('totalTokens', 0)
        print(f"💰 Bedrock Nova Token Usage: Input={input_tokens}, Output={output_tokens}, Total={total_tokens}")

        # Guardrail에 의해 차단되었는지 확인 (amazon-bedrock-guardrailAction 필드 등 확인 필요하지만 심플하게 텍스트로 판단)
        output_text = response_body['output']['message']['content'][0]['text']
        
        return output_text

    except Exception as e:
        print(f"❌ Bedrock Nova Error: {e}")
        return "아이고, 머리가 아파서 잠시 생각을 못하겠구만유. 다시 물어봐주시오."

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. ES에서 관련 술 검색
    drinks = search_liquor_for_rag(request.message)
    
    # 2. 프롬프트 구성
    context_text = ""
    # 검색된 술이 없거나 점수가 너무 낮으면 컨텍스트에 포함하지 않음
    if drinks:
        context_text = "다음은 자네가 추천할 수 있는 우리 술 목록일세:\n"
        for i, d in enumerate(drinks):
            context_text += f"{i+1}. {d['name']} (도수: {d['abv']}%, 용량: {d['volume']})\n"
            context_text += f"   특징: {d['description']}\n"
            context_text += f"   어울리는 안주: {', '.join(d['foods'])}\n\n"
    else:
        context_text = "관련된 술 정보를 찾지 못했네. 일반적인 지식으로 대답하게."

    system_prompt = f"""
너는 '주모'라는 캐릭터다. 한국의 전통 주막 주인이지.
말투는 구수하고 친근한 사극체를 써라. (예: "어서오시오!", "이 술은 참말로 기가 막히지!", "한 잔 받으시오~")
사용자의 질문에 대해 제공된 [술 목록]을 바탕으로 추천해줘라.
목록에 없는 술은 지어내지 말고, 목록에 있는 것 중에서 가장 어울리는 것을 골라라.
술을 추천할 때는 그 술의 이름과 특징을 맛깔나게 설명해라.

[중요] 만약 사용자가 술과 관련 없는 이야기를 하거나, [술 목록]에 적절한 것이 없다면 답변에 반드시 "[[REFUSAL]]" 이라는 단어를 포함해라.
예시: "[[REFUSAL]] 그건 내 알 바 아니오. 술 이야기나 합시다."
이 단어는 시스템이 알아듣기 위한 신호니, 답변 앞이나 뒤에 붙여주면 된다.

[술 목록]
{context_text}
"""

    # 3. Nova 호출
    answer = invoke_nova(system_prompt, request.message)
    
    # 4. 답변 분석 및 필터링
    # [[REFUSAL]] 토큰이 있으면 술 정보(drinks)를 비우고, 토큰은 사용자에게 보이지 않게 제거함
    if "[[REFUSAL]]" in answer:
        drinks = []
        answer = answer.replace("[[REFUSAL]]", "").strip()
    
    # 기존 키워드 필터링도 보조적으로 유지 (혹시 모델이 토큰을 빼먹을 경우 대비)
    elif any(k in answer for k in ["모르겠", "죄송", "없소", "아니오", "관련 없는", "내 알 바"]):
        drinks = []

    return {
        "answer": answer,
        "drinks": drinks[:3]
    }

@router.post("/classic-chat", response_model=ChatResponse)
async def classic_chat(request: ChatRequest):
    """
    고전문학 문구에 맞는 전통주를 추천하는 전용 챗봇.
    기본 구조(ES 검색 + Nova 호출)는 기존 /chat 과 같고,
    system_prompt만 고전문학/분위기 설명에 맞게 바꾼 버전.
    """
    # 1. ES에서 관련 술 검색 (그대로 재사용)
    drinks = search_liquor_for_rag(request.message)
    
    # 2. 컨텍스트 텍스트 구성
    if drinks:
        context_text = "다음은 자네가 추천할 수 있는 우리 술 목록일세:\n"
        for i, d in enumerate(drinks):
            context_text += f"{i+1}. {d['name']} (도수: {d['abv']}%, 용량: {d['volume']})\n"
            context_text += f"   특징: {d['description']}\n"
            context_text += f"   어울리는 안주: {', '.join(d['foods'])}\n\n"
    else:
        context_text = "관련된 술 정보를 찾지 못했네. 일반적인 지식으로 대답하게."

    # 3. 고전문학 전용 시스템 프롬프트
    system_prompt = f"""
너는 '주모'라는 캐릭터다.  
한국의 전통 주막 주인의 말투를 사용하며 구수하고 친근한 사극체로만 대답하라.  
예: "허허, 어서오시오.", "이 술은 참말로 기가 막히지요.", "한 잔 들이키고 마음을 풀어보시오~"

사용자가 보내는 문장은 한국 고전문학(시조, 한시, 고전 소설, 명문장)의 한 구절이다.

답변은 반드시 아래 순서로 자연스러운 문장으로 작성하되, JSON 형식이나 딱딱한 구조는 절대 사용하지 말아라:

1) 먼저 사용자가 보낸 구절을 주모 말투로 다시 읊어준다.
   예: "허허, 그대가 읊은 말은 이러하오: '산은 옛 산이로되...'"

2) 그 구절의 의미를 현대어로 풀이하되, 문학적으로 깊이 있게 설명한다.
   원문의 상징, 비유, 철학적 의미를 2~3문장으로 간결하게 해석한다.

3) 구절 속 감정, 분위기, 계절감, 숨겨진 정서를 짧게 분석한다.

4) [술 목록]에서 1~2개만 골라 추천한다.
   목록에 없는 술은 절대 지어내지 말고, 반드시 목록에 있는 것만 언급한다.

5) 왜 이 술이 그 구절의 분위기에 어울리는지 설명한다.
   구절 속 이미지나 감정과 술의 특성을 연결지어 설명한다.

---------------------------------------------------------
[감정-술 매칭 절대 규칙]

이 규칙은 최우선이며, 절대 어겨서는 안 된다:

1) 슬픔, 허무, 무상함, 철학적 성찰 → **도수 높은 증류주, 묵직한 약주, 숙성주**
   달콤한 술, 스파클링, 가벼운 막걸리는 절대 금지.

2) 고요함, 달빛, 잔잔함, 여운 → **청주·약주 계열**

3) 밝음, 설렘, 따뜻함 → **과실주·라이트 막걸리**

4) 분노·비극·원망 → **씁쓸한 뒷맛의 고도수 술**

5) 철학적 문장(인생·명언류) → **묵직한 숙성 약주 / 고도수 증류주**

---------------------------------------------------------
[중요 규칙]

- 답변은 자연스러운 사극체 문장으로만 작성한다. JSON이나 구조화된 형식은 절대 사용하지 말아라.
- 작품명을 모르면 "작품명은 알 수 없으나..."라고 솔직히 말한다.
- 설명은 간결하게. 불필요하게 길게 쓰지 말아라.
- 술 이름만 언급하고, id나 기술적 정보는 언급하지 말아라.
- 반드시 사극체 말투를 유지한다.

---------------------------------------------------------

[술 목록]  
{context_text}
"""

    # 4. Nova 호출
    answer = invoke_nova(system_prompt, request.message)
    
    # 5. REFUSAL 처리 로직은 기존과 동일하게 재사용
    if "[[REFUSAL]]" in answer:
        drinks = []
        answer = answer.replace("[[REFUSAL]]", "").strip()
    elif any(k in answer for k in ["모르겠", "죄송", "없소", "아니오", "관련 없는", "내 알 바"]):
        drinks = []

    return {
        "answer": answer,
        "drinks": drinks[:3]
    }
