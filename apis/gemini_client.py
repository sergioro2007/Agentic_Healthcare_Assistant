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
    # Make sure GOOGLE_API_KEY is set in your environment or .env file
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set it using: export GOOGLE_API_KEY='your-api-key'")
        exit(1)
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # List all available models
    print("Available Models:")
    for model in genai.list_models():
        print(f"- {model.name} ({model.display_name})")
        print(f"  Description: {model.description}")
