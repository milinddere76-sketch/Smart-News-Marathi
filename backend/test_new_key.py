import google.generativeai as genai
import os

key = "AIzaSyAFF8VQgeMi_akd70l67rmDvt7UhPT7-jg"
genai.configure(api_key=key)

try:
    print("Testing new Gemini key...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Say 'Key works in Marathi!' in Marathi.")
    if response and response.text:
        print(f"Success: {response.text}")
    else:
        print("Error: No text in response.")
except Exception as e:
    print(f"Error: {e}")
