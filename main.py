import os
import sys
import cv2
import tempfile
import time
from PIL import Image
from google import genai
from load_file import load_file
from get_api_key import get_api_key

PROMPT = load_file("prompt.txt")

def call_gemini_vision(api_key: str, img_path: str, prompt: str) -> str:
    """
    Send the image and prompt to the Google Generative AI library and return the model's reply.
    """
    img = Image.open(img_path)

    model_name = 'gemini-2.5-flash-lite'

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, img]
        )
        return response.text
    
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")


def main():
    # Check API key
    try:
        api_key = get_api_key()
    except EnvironmentError as e:
        print("API key error:", e)
        sys.exit(1)

    # Open the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam. Check camera access and device index.")
        sys.exit(1)

    overlay_text = ""
    overlay_until = 0

    print("Press SPACE to capture, press 'q' or ESC to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read from camera.")
                break

            # Display overlay text if set and not expired
            now = time.time()
            if overlay_text and now < overlay_until:
                # Draw a semi-transparent rectangle for readability
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (0, 0), (w, 50), (0, 0, 0), -1)
                cv2.putText(frame, overlay_text, (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            cv2.imshow("Camera", frame)

            key = cv2.waitKey(1) & 0xFF
            
            # Spacebar pressed
            if key == 32:
                # Save a temporary image file
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                    tmp_path = tf.name
                    cv2.imwrite(tmp_path, frame)

                try:
                    print("Analyzing with AI model...")
                    result = call_gemini_vision(api_key, tmp_path, PROMPT)

                    # Extract the first word and strip any punctuation (like "Trash." -> "Trash")
                    if isinstance(result, str):
                        printed = result.strip().split()[:1][0]
                        printed = "".join(c for c in printed if c.isalpha())
                    else:
                        printed = "Error"

                    overlay_text = printed
                    overlay_until = time.time() + 4.0  # show for 4 seconds

                    print("AI response:", printed)
                except Exception as e:
                    print("Error during API call:", e)
                    overlay_text = "API error"
                    overlay_until = time.time() + 4.0
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

            # Quit on 'q' or ESC
            if key == ord('q') or key == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
