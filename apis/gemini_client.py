"""
Client for interacting with the Google Gemini API.
"""
import os
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key=None):
        """
        Initializes the Gemini client.
        API key is retrieved from the GOOGLE_API_KEY environment variable if not provided.
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API key not provided or found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def generate_text(self, prompt):
        """
        Generates text using the Gemini model.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

if __name__ == '__main__':
    # Example usage:
    api_key_to_test = "AIzaSyBmFRX347NxFK3gVUzKLrCj_dGvWnd1FNg"
    
    # Configure the API
    genai.configure(api_key=api_key_to_test)
    
    # List all available models
    print("Available Models:")
    for model in genai.list_models():
        print(f"- {model.name} ({model.display_name})")
        print(f"  Description: {model.description}")
