import streamlit as st
from content_analyzer.analyzer import ContentAnalyser

st.set_page_config(layout="wide")

st.title("Enterprise Content Analysis Report")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("Select the analysis type and upload your content below.")
    analysis_type = st.selectbox(
        "Analysis Type",
        ("General Business", "Competitive Intelligence", "Customer Feedback")
    )
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


def display_analysis_results(analysis, analysis_type):
    st.markdown("### Analysis Report")
    for key, value in analysis.items():
        st.markdown(f"**{key.replace('_', ' ').title()}**")
        if isinstance(value, list):
            for item in value:
                st.markdown(f"- {item}")
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                st.markdown(f"  - **{sub_key.replace('_', ' ').title()}:** {sub_value}")
        else:
            st.markdown(value)


if analyze_button and uploaded_files:
    content_input = ""
    for uploaded_file in uploaded_files:
        content_input += uploaded_file.read().decode("utf-8") + "\n"
    try:
        analyser = ContentAnalyser()
    except ValueError as e:
        st.error(e)
        st.stop()

    with st.spinner(f"Analyzing content with {analysis_type} analysis..."):
        analysis = analyser.analyze_content(content_input, analysis_type)
        
        st.divider()
        st.subheader("Analysis Results")

        if "error" in analysis:
            st.error(analysis["error"])
        else:
            st.success("Analysis complete!")
            display_analysis_results(analysis, analysis_type)

elif analyze_button and not uploaded_files:
    st.warning("Please upload some content to analyze.")