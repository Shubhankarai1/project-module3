import streamlit as st
from content_analyzer.analyzer import ContentAnalyser

st.set_page_config(layout="wide")

st.title("Enterprise Content Analysis Report")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("Upload your content below for analysis.")
    uploaded_files = st.file_uploader("Content to analyze", accept_multiple_files=True, label_visibility="collapsed")
    
    analyze_button = st.button("Analyse")

with col2:
    st.subheader("Estimated Cost")
    if uploaded_files:
        total_size_in_bytes = sum(file.size for file in uploaded_files)
        total_size_in_mb = total_size_in_bytes / (1024 * 1024)
        cost = total_size_in_mb * 0.05
        st.info(f"Estimated cost for analyzing {len(uploaded_files)} file(s) ({total_size_in_mb:.2f} MB): **${cost:.4f}**")
    else:
        st.info("Each analysis costs an estimated **$0.05 per MB**.")
    
    st.subheader("About")
    st.write("This tool uses advanced AI to analyze your content, providing a summary, sentiment analysis, and key points.")


if analyze_button and uploaded_files:
    content_input = ""
    for uploaded_file in uploaded_files:
        content_input += uploaded_file.read().decode("utf-8") + "\n"
    try:
        analyser = ContentAnalyser()
    except ValueError as e:
        st.error(e)
        st.stop()

    with st.spinner("Analyzing..."):
        analysis = analyser.analyze_content(content_input)
        
        st.divider()
        st.subheader("Analysis Results")

        if "error" in analysis:
            st.error(analysis["error"])
        else:
            st.success("Analysis complete!")
            
            st.subheader("Executive Summary")
            st.write(analysis.get("executive_summary", "No summary provided."))

            st.subheader("Content Classification")
            classification = analysis.get("content_classification", {})
            st.write(f"**Type:** {classification.get('type', 'N/A')}")
            st.write(f"**Industry:** {classification.get('industry', 'N/A')}")
            st.write(f"**Quality Score:** {classification.get('quality_score', 'N/A')}")

            st.subheader("Sentiment Analysis")
            sentiment = analysis.get("sentiment_analysis", {})
            st.write(f"**Sentiment:** {sentiment.get('sentiment', 'N/A')}")
            st.write(f"**Confidence Score:** {sentiment.get('confidence_score', 'N/A')}")

            st.subheader("Key Insight Extraction")
            insights = analysis.get("key_insight_extraction", [])
            if insights:
                for insight in insights:
                    st.markdown(f"- **Finding:** {insight.get('finding', 'N/A')} | **Impact:** {insight.get('impact_level', 'N/A')}")
            else:
                st.write("No key insights provided.")

            st.subheader("Strategic Implications")
            st.write(analysis.get("strategic_implications", "No strategic implications provided."))

            st.subheader("Risks")
            st.write(analysis.get("risks", "No risks provided."))

            st.subheader("Action Items")
            action_items = analysis.get("action_items", [])
            if action_items:
                for item in action_items:
                    st.markdown(f"- **Item:** {item.get('item', 'N/A')} | **Priority:** {item.get('priority', 'N/A')}")
            else:
                st.write("No action items provided.")

            with st.expander("Full JSON Response"):
                st.json(analysis)

elif analyze_button and not uploaded_files:
    st.warning("Please upload some content to analyze.")