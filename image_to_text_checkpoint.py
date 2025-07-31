from dotenv import load_dotenv
import os
import google.generativeai as genai
import PIL.Image

def to_markdown(text):
    if text.strip():
        text = text.replace('•', '*')
        # Clean up common OCR response prefixes
        if text.startswith('The medicine is '):
            text = text[len('The medicine is '):]
        if text.startswith('This is an image of '):
            text = text[len('This is an image of '):]
        return text.strip()
    else:
        return "No text could be extracted from the image. Please try again."

# Load API key from environment file
load_dotenv('key.env')
api_key = os.getenv('API_KEY')

if api_key:
    # Clean up the key if it has extra characters (optional but good practice)
    api_key = api_key.replace('<', '').replace('>', '')
    genai.configure(api_key=api_key)
else:
    print("API_KEY not found in key.env file.")

# Model configuration
config = {
  'temperature': 0.5,
  'top_k': 32,
  'top_p': 1,
  'max_output_tokens': 4096,
}




def image_to_text(file_path):

    """
    Extracts text from an image and returns None on failure.
    """

    if not api_key:
        print("API key is not configured.")
        return None

    try:
        img = PIL.Image.open(file_path)
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=config
        )
        
        prompt = "Extract only the name of the medicine from this image. Do not add any extra text or explanation."
        response = model.generate_content([prompt, img])
        
        if response.text:
            return to_markdown(response.text)
        else:
            return None # Return None if model gives no response

    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return None # Return None on any error
