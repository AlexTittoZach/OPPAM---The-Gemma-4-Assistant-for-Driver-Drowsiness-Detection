import cv2
import google.generativeai as genai
import time
import winsound
import pyttsx3
import io
import threading

# --- 1. SETUP API & MODEL ---

GOOGLE_API_KEY = "Replace_with_your_actual_api_key"

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemma-4-26b-a4b-it')

# --- 2. GLOBAL SYSTEM STATES ---
current_frame = None
last_status = "INITIALIZING..."
is_running = True
ai_ready = True  
is_alarm_active = False  

# --- 3. AUDIO ALARM LOOP ---
def continuous_alarm_loop():
    global is_alarm_active, is_running
    
    voice_engine = pyttsx3.init()
    voice_engine.setProperty('rate', 165)
    
    while is_running:
        if is_alarm_active:
            print("🚨 [ALARM EVENT ACTIVE] Triggering audio loops...")
            winsound.Beep(1100, 350)
            
            try:
                voice_engine.say("Please take a break, you are about to sleep")
                voice_engine.runAndWait()
            except Exception:
                voice_engine = pyttsx3.init()
                voice_engine.setProperty('rate', 165)
                
            time.sleep(0.1)
        else:
            time.sleep(0.2)

# --- 4. OPTIMIZED MEMORY-BASED GEMMA 4 VISION THREAD ---
def process_latest_frame():
    global last_status, current_frame, ai_ready, is_alarm_active
    
    if current_frame is None or not ai_ready:
        return

    ai_ready = False  
    
    try:
        # Rotate image to keep orientation vertical
        rotated_frame = cv2.rotate(current_frame, cv2.ROTATE_90_CLOCKWISE)

        success, encoded_image = cv2.imencode('.jpg', rotated_frame)
        if not success:
            ai_ready = True
            return
            
        image_bytes = encoded_image.tobytes()
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }

        prompt = (
            "You are a strict biometric sensor. Analyze the driver's face. "
            "If their eyes are closed/heavy or they are yawning, reply ONLY with the word 'TIRED'. "
            "Otherwise, reply ONLY with the word 'SAFE'. Do not think out loud. Do not output paragraphs."
        )
        
        response = model.generate_content(
            [prompt, image_part],
            generation_config=genai.GenerationConfig(
                max_output_tokens=30,  # Increased slightly to give the final token safety room
                temperature=0.0
            )
        )
        
        # Clean up the output string block completely
        raw_output = response.text.strip().upper()
        print(f"[GEMMA 4 DATA LOG] Raw Response:\n{raw_output}")

        # STABLE PARSING FIX: Split output by lines and evaluate the very last line printed
        lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
        final_decision = lines[-1] if lines else ""
        
        print(f"[PARSING LOG] Evaluated Final Line: '{final_decision}'")

        # Check if the final word matches our trigger conditions precisely
        if "TIRED" in final_decision:
            last_status = "🚨 CRITICAL: FATIGUE DETECTED 🚨"
            is_alarm_active = True  
        else:
            last_status = "STATUS: SAFE"
            is_alarm_active = False  
            
    except Exception as e:
        print(f"Gemma 4 API Exception: {e}")
        
    ai_ready = True  

def ai_scheduler():
    while is_running:
        if ai_ready:
            threading.Thread(target=process_latest_frame, daemon=True).start()
        time.sleep(0.8)

# --- 5. GRAPHICAL PRESENTATION INTERFACE ---
url = "http://10.62.181.182:8080/video"
cap = cv2.VideoCapture(url)

threading.Thread(target=ai_scheduler, daemon=True).start()
threading.Thread(target=continuous_alarm_loop, daemon=True).start()

print("--- Guardian Eye: Pure Gemma 4 Low-Latency System ONLINE ---")

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    current_frame = frame

    color = (0, 255, 0) if "SAFE" in last_status else (0, 0, 255)
    cv2.putText(frame, last_status, (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Guardian Eye Pro", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        is_running = False
        is_alarm_active = False
        break

cap.release()
cv2.destroyAllWindows()