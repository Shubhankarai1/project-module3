import streamlit as st
from content_analyzer.analyzer import analyze_content

st.title("Enterprise Content Analysis Platform")

st.write("Analyze your business documents using AI.")

uploaded_file = st.file_uploader("Choose a document to analyze", type=["txt", "md"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.text_area("Document Content", content, height=300)

    if st.button("Analyze Content"):
        with st.spinner("Analyzing..."):
            analysis = analyze_content(content)
            st.subheader("Analysis Results")
            st.write(analysis)
