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
            # Clean text for better search
            import re
            # Remove common keywords that might confuse search
            keywords_to_remove = ["막걸리", "약주", "청주", "소주", "과실주", "리큐르", "ALC", "VOL", "%", "ML", "L", "ml", "l"]
            cleaned_text = detected_text
            for kw in keywords_to_remove:
                cleaned_text = re.sub(kw, "", cleaned_text, flags=re.IGNORECASE)
            
            # Remove special characters but keep Hangul and spaces
            # cleaned_text = re.sub(r"[^가-힣\s]", "", cleaned_text) # Too aggressive?
            
            # Blocklist to filter out instructional/warning text
            blocklist = [
                "개봉", "보관", "반품", "유통기한", "경고", "지나친", "음주", "청소년", "임신", 
                "원재료", "업소명", "소재지", "내용량", "식품유형", "고객", "상담", "신고", 
                "불량식품", "뚜껑", "취급", "교환", "환불", "소비자", "분쟁", "해결", "기준", "의거"
            ]
            
            # Just take the first line or first few words as it's usually the name
            lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
            
            # Strategy: Prioritize Korean lines that are NOT in the blocklist
            valid_korean_lines = []
            for line in lines:
                if re.search(r'[가-힣]', line):
                    # Check if line contains any blocklist keyword
                    if not any(keyword in line for keyword in blocklist):
                        valid_korean_lines.append(line)
            
            if valid_korean_lines:
                # If we have valid Korean lines, use the first one
                search_query = valid_korean_lines[0]
                # If the first line is very short (e.g., "지란"), append the second valid line if available
                if len(valid_korean_lines) > 1 and len(search_query) < 5: 
                     search_query += " " + valid_korean_lines[1]
            elif lines:
                # Fallback to first line if no valid Korean lines found (or all filtered out)
                # Still try to avoid blocklisted lines if possible
                valid_lines = [line for line in lines if not any(keyword in line for keyword in blocklist)]
                if valid_lines:
                    search_query = valid_lines[0]
                else:
                    search_query = lines[0] # Last resort
                
                if len(lines) > 1 and len(search_query) < 3:
                    search_query += " " + lines[1]
            else:
                search_query = cleaned_text[:20]

            print(f"🔍 Search Query: '{search_query}'")
            search_result = search_liquor_fuzzy(search_query)
            
            # [NEW] Romanization Support (Hangulize)
            # If no result found AND query is English, try converting to Hangul
            if not search_result and re.match(r'^[a-zA-Z0-9\s\.,]+$', search_query):
                try:
                    from hangulize import hangulize
                    # Use 'ita' (Italian) as a proxy for phonetic reading of Romanized words
                    # 'eng' is often not available or too complex for simple transliteration
                    hangul_query = hangulize(search_query, 'ita') 
                    print(f"🔤 Hangulized Query: '{search_query}' -> '{hangul_query}'")
                    
                    # Search again with Hangulized query
                    hangul_search_result = search_liquor_fuzzy(hangul_query)
                    if hangul_search_result:
                        search_result = hangul_search_result
                        print(f"✅ Hangulized Match Found: '{search_result['name']}'")
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
