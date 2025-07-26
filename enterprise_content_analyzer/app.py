import streamlit as st
from content_analyzer.analyzer import ContentAnalyser

st.title("Enterprise Content Analysis Platform")

st.write("Analyze your business documents using AI.")

# Instantiate the analyser
try:
    analyser = ContentAnalyser()
except ValueError as e:
    st.error(e)
    st.stop()

uploaded_file = st.file_uploader("Choose a document to analyze", type=["txt", "md"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.text_area("Document Content", content, height=300)

    if st.button("Analyze Content"):
        with st.spinner("Analyzing..."):
            analysis = analyser.analyze_content(content)
            st.subheader("Analysis Results")
            if "error" in analysis:
                st.error(analysis["error"])
            else:
                st.success("Analysis complete!")
                st.subheader("Summary")
                st.write(analysis.get("summary", "No summary provided."))
                st.subheader("Sentiment")
                st.write(analysis.get("sentiment", "No sentiment provided."))
                st.subheader("Key Points")
                key_points = analysis.get("key_points", [])
                if key_points:
                    for point in key_points:
                        st.markdown(f"- {point}")
                else:
                    st.write("No key points provided.")
