
import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()

class ContentAnalyser:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        openai.api_key = self.api_key

    def analyze_content(self, text: str) -> dict:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content analyzer. Analyze the following text and provide a summary, sentiment (positive, neutral, or negative), and 3 key points. Format the output as a JSON object with the keys 'summary', 'sentiment', and 'key_points'."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except openai.APIError as e:
            # Handle API errors (e.g., network issues, server errors)
            return {"error": f"OpenAI API error: {e}"}
        except json.JSONDecodeError:
            # Handle cases where the response is not valid JSON
            return {"error": "Failed to decode JSON response from the API."}
        except Exception as e:
            # Handle other potential errors
            return {"error": f"An unexpected error occurred: {e}"}
