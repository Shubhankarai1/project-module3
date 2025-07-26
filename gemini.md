# Enterprise Content Analysis Platform

This document outlines the plan for creating the Enterprise Content Analysis Platform.

## Project Structure

```
.
├── app.py
├── content_analyzer
│   ├── __init__.py
│   └── analyzer.py
├── .env.example
├── README.md
└── requirements.txt
```

## Plan

1.  Create the project directory `enterprise_content_analyzer`.
2.  Create the files and directories as outlined in the project structure.
3.  Provide instructions for setting up the virtual environment and installing dependencies using `uv`.
4.  Create a Streamlit app with a professional title, a text area for content, an “Analyse” button, and a display for the analysis results.
5.  The application will support three types of analysis: General Business, Competitive Intelligence, and Customer Feedback.
6.  A dropdown menu in the Streamlit interface will allow users to select the desired analysis type.
7.  Each analysis type will have a specific prompt template that structures the output in JSON format.
    -   **General Business:** Focuses on content classification, key insights, sentiment, strategic implications, risks, and action items.
    -   **Competitive Intelligence:** Concentrates on competitor identification, market positioning, and threat analysis.
    -   **Customer Feedback:** Centers on sentiment analysis, pain point identification, and feature requests.
8.  The analysis results will be displayed in a structured JSON format in the Streamlit app.