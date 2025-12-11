from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import httpx
import os
import json
import uuid
import time
import base64
import google.generativeai as genai

router = APIRouter()

CLOVA_OCR_API_URL = os.getenv("CLOVA_OCR_API_URL")
CLOVA_OCR_SECRET_KEY = os.getenv("CLOVA_OCR_SECRET_KEY")

from app.utils.search_stats import save_search_query

async def process_clova_ocr(content: bytes, filename: str):
    if not CLOVA_OCR_API_URL or not CLOVA_OCR_SECRET_KEY:
        raise HTTPException(status_code=500, detail="OCR configuration missing")

    try:
        # Prepare request for Clova OCR
        request_json = {
            "images": [
                {
                    "format": filename.split(".")[-1] if "." in filename else "jpg",
                    "name": "demo",
                    "data": base64.b64encode(content).decode("utf-8")
                }
            ],
            "requestId": str(uuid.uuid4()),
            "version": "V2",
            "timestamp": int(round(time.time() * 1000))
        }

        headers = {
            "X-OCR-SECRET": CLOVA_OCR_SECRET_KEY,
            "Content-Type": "application/json"
        }

        # Enforce HTTPS
        api_url = CLOVA_OCR_API_URL
        if api_url.startswith("http://"):
            api_url = api_url.replace("http://", "https://")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=request_json
            )
            
            if response.status_code != 200:
                print(f"OCR Error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="OCR service error")

            result = response.json()
            
            # Extract text from response
            detected_text = []
            for image in result.get("images", []):
                for field in image.get("fields", []):
                    detected_text.append(field.get("inferText", ""))
            
            return {
                "success": True,
                "text": " ".join(detected_text),
                "raw_result": result
            }

    except Exception as e:
        import traceback
        print(f"Error processing Clova OCR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Clova OCR Error: {str(e)}")

def process_gemini_ocr(content: bytes):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key is missing")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Convert bytes to a format Gemini accepts (e.g., PIL Image or direct bytes part)
        # Gemini Python SDK supports passing a dict with 'mime_type' and 'data'
        
        image_part = {
            "mime_type": "image/jpeg", # Assuming JPEG for simplicity, or detect
            "data": content
        }
        
        prompt = "Extract all text from this image. Output only the extracted text."
        
        start_time = time.time()
        response = model.generate_content([prompt, image_part])
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"⏱️ Gemini OCR Time: {elapsed_time:.2f}s")
        
        if response.usage_metadata:
            print(f"💰 Gemini OCR Token Usage: Input={response.usage_metadata.prompt_token_count}, Output={response.usage_metadata.candidates_token_count}, Total={response.usage_metadata.total_token_count}")
            
        text = response.text
        
        return {
            "success": True,
            "text": text.strip(),
            "raw_result": {"text": text}
        }
    except Exception as e:
        print(f"Gemini OCR Error: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini OCR Error: {str(e)}")

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    provider: str = Form("clova")
):
    try:
        # Read file content
        content = await file.read()
        
        result = {}
        if provider == "gemini":
            result = process_gemini_ocr(content)
        elif provider == "clova":
            result = await process_clova_ocr(content, file.filename)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

        print(f"[{provider.upper()}] Detected Text: {result.get('text', 'No text detected')}")
        
        # [NEW] Fuzzy Search Integration
        from app.api.search import search_liquor_fuzzy
        detected_text = result.get('text', '')
        if detected_text:
            import re
            
            # Blocklist to filter out instructional/warning text (keep this)
            blocklist = [
                "개봉", "보관", "반품", "유통기한", "경고", "지나친", "음주", "청소년", "임신", 
                "원재료", "업소명", "소재지", "내용량", "식품유형", "고객", "상담", "신고", 
                "불량식품", "뚜껑", "취급", "교환", "환불", "소비자", "분쟁", "해결", "기준", "의거",
                "100%", "우리쌀", "빚은", "증류식", "명품", "참좋은", "전통", "방식"
            ]
            
            # Split into lines
            lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
            
            # Strategy 1: Find Korean product names (usually 2-6 characters)
            # Look for patterns like "안동소주", "백세주", "이화주" etc.
            product_name_candidates = []
            
            for line in lines:
                # Skip lines with blocklist keywords
                if any(keyword in line for keyword in blocklist):
                    continue
                
                # Skip lines with percentage, ml, alcohol content
                if re.search(r'\d+%|\d+ml|alc\.|vol\.', line, re.IGNORECASE):
                    continue
                    
                # Extract Korean phrases (2-10 characters)
                korean_phrases = re.findall(r'[가-힣]{2,10}', line)
                
                # Also extract English words (for romanized matching)
                english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', line)
                
                # Process Korean phrases
                for phrase in korean_phrases:
                    # Skip common generic words ONLY if they appear alone
                    if phrase in ["막걸리", "약주", "청주", "과실주", "리큐르"]:
                        continue
                    
                    # Priority: lines with regional names + product type (e.g., "안동소주", "경주법주")
                    if any(region in phrase for region in ["안동", "경주", "문배", "진주", "이강", "양촌", "서울"]):
                        product_name_candidates.insert(0, phrase)  # High priority
                    else:
                        product_name_candidates.append(phrase)
                
                # Process English words (rely on ES romanized field)
                for word in english_words:
                    # Skip common English words that aren't product names
                    if word.lower() in ['the', 'and', 'for', 'with', 'alcohol', 'traditional', 'korean', 'rice', 'wine', 'beer', 'spirits']:
                        continue
                    # Add English candidates (ES will match via romanized field)
                    product_name_candidates.append(word)
            
            # Strategy 2: If no good candidates, use first valid Korean line
            if not product_name_candidates:
                for line in lines:
                    if re.search(r'[가-힣]', line):
                        if not any(keyword in line for keyword in blocklist):
                            # Extract just Korean characters
                            korean_only = re.sub(r'[^가-힣\s]', '', line).strip()
                            if korean_only and len(korean_only) >= 2:
                                product_name_candidates.append(korean_only)
                                break
            
            # Choose the best candidate
            if product_name_candidates:
                search_query = product_name_candidates[0]
            elif lines:
                # Last resort: use first non-blocklisted line
                valid_lines = [line for line in lines if not any(keyword in line for keyword in blocklist)]
                search_query = valid_lines[0] if valid_lines else lines[0]
            else:
                search_query = detected_text[:20]

            print(f"🔍 Search Query: '{search_query}'")
            search_result = search_liquor_fuzzy(search_query)
            
            # [NEW] Romanization Support (Hangulize + Custom Mapping)
            # If no result found AND query is English, try converting to Hangul
            if not search_result and re.match(r'^[a-zA-Z0-9\s\.,]+$', search_query):
                # Custom mapping for common traditional liquor names
                custom_romanization = {
                    "geisha": "게이샤",
                    "baekseju": "백세주",
                    "makgeolli": "막걸리",
                    "hwayo": "화요",
                    "andong": "안동",
                    "gyeongju": "경주",
                    "chamisul": "참이슬",
                    "jinro": "진로",
                    "bokbunja": "복분자",
                    "soju": "소주",
                    "yakju": "약주",
                    "cheongju": "청주",
                }
                
                # Try custom mapping first
                query_lower = search_query.lower().strip()
                if query_lower in custom_romanization:
                    hangul_query = custom_romanization[query_lower]
                    print(f"🗺️ Custom Mapping: '{search_query}' -> '{hangul_query}'")
                    search_result = search_liquor_fuzzy(hangul_query)
                    if search_result:
                        print(f"✅ Custom Match Found: '{search_result['name']}'")
                
                # If custom mapping didn't work, try Hangulize with multiple languages
                if not search_result:
                    try:
                        from hangulize import hangulize
                        # Try multiple language profiles
                        language_profiles = ['jpn', 'eng', 'ita']  # Japanese, English, Italian
                        
                        for lang in language_profiles:
                            try:
                                hangul_query = hangulize(search_query, lang)
                                print(f"🔤 Hangulize ({lang}): '{search_query}' -> '{hangul_query}'")
                                
                                # Search with hangulized query
                                hangul_search_result = search_liquor_fuzzy(hangul_query)
                                if hangul_search_result:
                                    search_result = hangul_search_result
                                    print(f"✅ Hangulize Match Found ({lang}): '{search_result['name']}'")
                                    break
                            except Exception as lang_err:
                                print(f"⚠️ Hangulize {lang} failed: {lang_err}")
                                continue
                                
                    except Exception as e:
                        print(f"⚠️ Hangulize Error: {e}")

            if search_result:
                result['search_result'] = search_result
                print(f"✅ ES Match Found: '{search_result['name']}' (Score: {search_result['score']})")
                
                # [NEW] Log the successful search for aggregation
                try:
                    await save_search_query(search_result['name'], drink_id=search_result.get('id') or search_result.get('drink_id'))
                    print(f"📊 Search Aggregation Logged: {search_result['name']}")
                except Exception as log_err:
                    print(f"⚠️ Failed to log search stats: {log_err}")

                if 'candidates' in search_result:
                    print("   [Candidates]")
                    for cand in search_result['candidates']:
                        print(f"   - {cand['name']} (Score: {cand['score']})")
            else:
                print("  -> No matching liquor found in DB")

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"General Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
