import os
import openai
from dotenv import load_dotenv
import json
import time
from datetime import datetime

load_dotenv()

class ContentAnalyser:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        openai.api_key = self.api_key

        self.prompt_templates = {
            "General Business": {
                "content_classification": {
                    "type": "e.g., Financial Report, Customer Feedback, News Article",
                    "industry": "e.g., Technology, Healthcare, Finance",
                    "quality_score": "Score from 0.0 to 1.0"
                },
                "key_insight_extraction": [
                    {
                        "finding": "Insight 1",
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
                    }
                ],
                "business_impact": "e.g., High, Medium, Low",
                "executive_summary": "A concise summary of the most critical insights and recommendations."
            },
            "Competitive Intelligence": {
                "competitor_identification": [
                    {
                        "name": "Competitor Name",
                        "market_share": "e.g., 25%",
                        "key_strengths": ["Strength 1", "Strength 2"],
                        "key_weaknesses": ["Weakness 1", "Weakness 2"]
                    }
                ],
                "market_positioning": {
                    "our_position": "e.g., Market Leader, Niche Player",
                    "competitor_landscape": "e.g., Highly fragmented, Dominated by a few key players"
                },
                "threat_analysis": [
                    {
                        "threat": "e.g., New entrant, Price war",
                        "level": "High, Medium, or Low",
                        "mitigation_strategy": "e.g., Increase marketing spend, Focus on product differentiation"
                    }
                ],
                "opportunity_analysis": [
                    {
                        "opportunity": "e.g., Untapped market segment, Competitor weakness",
                        "potential_impact": "High, Medium, or Low",
                        "recommendation": "e.g., Launch a targeted marketing campaign, Develop a new feature"
                    }
                ],
                "sentiment_analysis": {
                    "sentiment": "Positive, Negative, or Neutral",
                    "confidence_score": "Score from 0.0 to 1.0"
                },
                "business_impact": "e.g., High, Medium, Low",
                "executive_summary": "A concise summary of the competitive landscape, key threats, and strategic opportunities."
            },
            "Customer Feedback": {
                "sentiment_analysis": {
                    "overall_sentiment": "Positive, Negative, or Neutral",
                    "confidence_score": "Score from 0.0 to 1.0",
                    "sentiment_distribution": {
                        "positive": "e.g., 60%",
                        "negative": "e.g., 30%",
                        "neutral": "e.g., 10%"
                    }
                },
                "pain_point_identification": [
                    {
                        "pain_point": "e.g., Difficult to use interface, Poor customer service",
                        "frequency": "e.g., 25 mentions",
                        "severity": "High, Medium, or Low"
                    }
                ],
                "feature_requests": [
                    {
                        "feature": "e.g., Dark mode, Integration with other tools",
                        "request_count": "e.g., 15 mentions",
                        "priority": "High, Medium, or Low"
                    }
                ],
                "satisfaction_drivers": [
                    "e.g., Ease of use",
                    "e.g., Excellent customer support"
                ],
                "actionable_recommendations": [
                    {
                        "recommendation": "e.g., Redesign the user interface, Improve customer service training",
                        "impact": "High, Medium, or Low",
                        "effort": "High, Medium, or Low"
                    }
                ],
                "business_impact": "e.g., High, Medium, Low",
                "executive_summary": "A concise summary of customer sentiment, key pain points, and actionable recommendations."
            }
        }

    def analyze_content(self, text: str, analysis_type: str) -> dict:
        if analysis_type not in self.prompt_templates:
            raise ValueError(f"Invalid analysis type: {analysis_type}")

        template = self.prompt_templates[analysis_type]
        
        prompt = f"""Please analyze the following text based on the "{analysis_type}" analysis type and provide a detailed analysis in JSON format. The analysis should follow this structure:

{json.dumps(template, indent=2)}

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
                        "content": f"You are an expert content analyzer specializing in {analysis_type} analysis. Your task is to provide a detailed, structured analysis of the given text in JSON format. Adhere strictly to the provided template."
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
            return {"error": f"OpenAI API error: {e}"}
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON response from the API."}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}

    def batch_analyze(self, documents: list, analysis_type: str, progress_callback=None):
        results = []
        total_documents = len(documents)
        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{i}")
            text = doc.get("text", "")
            
            if not text:
                results.append({"id": doc_id, "timestamp": datetime.now().isoformat(), "error": "Document text is empty."})
                if progress_callback:
                    progress_callback(i + 1, total_documents)
                continue

            try:
                analysis_result = self.analyze_content(text, analysis_type)
                results.append({"id": doc_id, "timestamp": datetime.now().isoformat(), "analysis": analysis_result})
            except Exception as e:
                results.append({"id": doc_id, "timestamp": datetime.now().isoformat(), "error": f"Analysis failed: {e}"})
            
            time.sleep(0.5) # Rate limiting
            
            if progress_callback:
                progress_callback(i + 1, total_documents)
        return results