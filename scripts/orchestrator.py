import time
import sys
import os

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from member2_platform_integration.platform_scrapers import DummyPlatformScraper
from member2_platform_integration.faiss_search_engine import FaissSearchEngine
from member3_detection.inference import DetectionInferenceEngine
from member4_automation_compliance.takedown_manager import TakedownManager

def run_pipeline():
    print("INIT: Deepfake Detection Multi-Module Pipeline Started.")
    
    scraper = DummyPlatformScraper()
    # Mocking protected persons
    PROTECTED_VICTIMS = ["ananya_v", "priya_v", "megha_v", "sara_v", "tanvi_v"]
    
    inference_engine = DetectionInferenceEngine()
    takedown_mgr = TakedownManager()
    
    processed_posts = set()

    try:
        while True:
            # 1. Fetch posts from Dummy Social Network
            posts = scraper.fetch_new_posts()
            new_posts = [p for p in posts if p['post_id'] not in processed_posts]
            
            if not new_posts:
                print(".", end="", flush=True)
                time.sleep(5)
                continue
            
            print(f"\nMEMBER 2: Found {len(new_posts)} new posts to scrape.")
            
            for post in new_posts:
                post_id = post['post_id']
                processed_posts.add(post_id)
                
                print(f"\n--- Analyzing Post {post_id} by {post['username']} ---")
                
                # MOCK FACIAL MATCH LOGIC:
                # In a real system, we'd use FaceNet + FAISS.
                # Here we check if any protected name is in the caption or if they are the author.
                caption = post.get('caption', '').lower()
                is_match = any(v.split('_')[0] in caption for v in PROTECTED_VICTIMS) or post['username'] in PROTECTED_VICTIMS
                
                if is_match:
                    matched_user = next((v for v in PROTECTED_VICTIMS if v.split('_')[0] in caption or v == post['username']), "unknown")
                    print(f"MEMBER 2: Facial match found for victim `{matched_user}`.")
                    
                    # Form Payload For Downstream Modules
                    case_payload = {
                        "platform": "dummy",
                        "post_id": post_id,
                        "url": post['image_url'],
                        "user_id": matched_user,
                        "confidence": 0.98
                    }
                    
                    # 2. Member 3: Detection Phase
                    print("MEMBER 3: Running Deepfake & Nudity Models...")
                    detection_res = inference_engine.analyze(image_path=post['image_url'])
                    
                    df_score = detection_res['deepfake']['score']
                    nude_score = detection_res['nudity']['score']
                    risk = detection_res['overall_risk_level']
                    print(f"   -> Deepfake: {df_score:.2f} | Nudity: {nude_score:.2f} | Risk: {risk.upper()}")
                    
                    # 3. Member 4: Compliance and Action
                    print("MEMBER 4: Processing Case...")
                    final_action = takedown_mgr.process_case(case_payload, detection_res)
                    
                    status = final_action.get("status")
                    reason = final_action.get("reason")
                    print(f"RESULT: {status} - {reason}")
                else:
                    print(f"MEMBER 2: No protected faces matched in post {post_id}.")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")

if __name__ == "__main__":
    run_pipeline()
