
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
        ANALYSIS_TEMPLATE = {
    "content_classification": {
        "type": "e.g., Financial Report, Customer Feedback, News Article",
        "industry": "e.g., Technology, Healthcare, Finance",
        "quality_score": "Score from 0.0 to 1.0"
    },
    "key_insight_extraction": [
        {
            "finding": "Insight 1",
            "impact_level": "High, Medium, or Low"
        },
        {
            "finding": "Insight 2",
            "impact_level": "High, Medium, or Low"
        },
        {
            "finding": "Insight 3",
            "impact_level": "High, Medium, or Low"
        }
    ],
    "sentiment_analysis": {
        "sentiment": "Positive, Negative, or Neutral",
        "confidence_score": "Score from 0.0 to 1.0"
    },
    "strategic_implications": "e.g., Potential for new market entry, need for product improvement",
    "risks": "e.g., Competitive threats, operational challenges",
    "action_items": [
        {
            "item": "Action 1",
            "priority": "High, Medium, or Low"
        },
        {
            "item": "Action 2",
            "priority": "High, Medium, or Low"
        }
    ],
    "executive_summary": "A concise summary of the most critical insights and recommendations."
}

        prompt = f"""
Please analyze the following text and provide a detailed analysis in JSON format. The analysis should follow this structure:

{json.dumps(ANALYSIS_TEMPLATE, indent=2)}

Here is the text to analyze:
---
{text}
---
"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content analyzer. Your task is to provide a detailed, structured analysis of the given text in JSON format. Adhere strictly to the provided template."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
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
