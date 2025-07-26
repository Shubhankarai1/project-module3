# Enterprise Content Analysis Platform

This document outlines the plan for creating the Enterprise Content Analysis Platform.

## Project Structure

```
.
├── app.py
├── content_analyzer
│   ├── __init__.py
│   ├── analyzer.py
│   ├── document_processor.py
│   └── cost_tracker.py
├── .env.example
├── README.md
└── requirements.txt
```

## Plan

1.  Create the project directory `enterprise_content_analyzer`.
2.  Create the files and directories as outlined in the project structure.
3.  Provide instructions for setting up the virtual environment and installing dependencies using `uv`.
4.  Create a Streamlit app with a professional title, a file uploader for documents, an “Analyse” button, and a display for the analysis results.
    -   **Updated**: The Streamlit app now includes tabs for "Single Analysis" and "Batch Processing".
5.  Implement a `DocumentProcessor` class to handle PDF, DOCX, and TXT files, extracting and cleaning text, optimizing content length (max 3000 tokens), and counting tokens using `tiktoken`. It will also return document metadata (type, size, token count).
6.  The application will support three types of analysis: General Business, Competitive Intelligence, and Customer Feedback.
7.  A dropdown menu in the Streamlit interface will allow users to select the desired analysis type.
8.  Each analysis type will have a specific prompt template that structures the output in JSON format.
    -   **General Business:** Focuses on content classification, key insights, sentiment, strategic implications, risks, action items, and now includes **Business Impact**.
    -   **Competitive Intelligence:** Concentrates on competitor identification, market positioning, threat analysis, opportunity analysis, and now includes **Sentiment Analysis** and **Business Impact**.
    -   **Customer Feedback:** Centers on sentiment analysis, pain point identification, feature requests, satisfaction drivers, actionable recommendations, and now includes **Business Impact**.
9.  Implement a `CostTracker` class to track daily and monthly API usage, save data to a JSON file, and calculate costs based on OpenAI pricing (with placeholder values for now).
10. Set daily budget limit to $450 and monthly to $2000.
11. Display remaining budget in the Streamlit sidebar.
12. Check if an analysis can be afforded before processing.
13. The analysis results will be displayed in a structured JSON format in the Streamlit app.
    -   **Updated**: Batch processing results are displayed in a pandas DataFrame with columns: Document, Type, Sentiment, Business Impact, Confidence, Cost.
14. Implement a `batch_analyze` method in `ContentAnalyser` to process multiple documents, including progress tracking and rate limiting (0.5 seconds delay between requests).
15. Return analysis results with document IDs and timestamps.
16. Handle errors gracefully during batch processing, continuing if one document fails.
17. Add a progress bar in the Streamlit app using `st.progress()` for batch analysis.
18. **New**: Add a download button for CSV export of batch analysis results.
19. **New**: Calculate and display total cost and average confidence for batch analysis.
20. **New**: Add an "Analytics" tab with interactive visualizations using Plotly:
    -   Sentiment distribution pie chart
    -   Business impact bar chart
    -   Confidence score histogram
    -   Cost per document analysis
    -   Content type breakdown