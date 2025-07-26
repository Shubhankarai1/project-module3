import streamlit as st
from content_analyzer.analyzer import ContentAnalyser
from content_analyzer.document_processor import DocumentProcessor
from content_analyzer.cost_tracker import CostTracker
import os
import tempfile

st.set_page_config(layout="wide")

st.title("Enterprise Content Analysis Report")

# Initialize session state
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None

# Initialize CostTracker
cost_tracker = CostTracker()

# Display remaining budget in the sidebar
st.sidebar.subheader("Budget Information")
st.sidebar.write(f"Daily Remaining: **${cost_tracker.get_remaining_daily_budget():.2f}**")
st.sidebar.write(f"Monthly Remaining: **${cost_tracker.get_remaining_monthly_budget():.2f}**")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("Select the analysis type and upload your document below.")
    analysis_type = st.selectbox(
        "Analysis Type",
        ("General Business", "Competitive Intelligence", "Customer Feedback")
    )
    
    uploaded_file = st.file_uploader(
        "Upload a document to analyze",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=False
    )

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            processor = DocumentProcessor()
            st.session_state.processed_text, st.session_state.metadata = processor.process_file(tmp_file_path)
        except Exception as e:
            st.error(f"Error processing file: {e}. Please ensure it's a valid PDF, DOCX, or TXT file.")
            st.session_state.processed_text = None
            st.session_state.metadata = None
        finally:
            os.remove(tmp_file_path)

    analyze_button = st.button("Analyse")

with col2:
    st.subheader("Document Details")
    if st.session_state.metadata:
        metadata = st.session_state.metadata
        st.info(
            f"**File Type:** {metadata['type']}  \n"
            f"**File Size:** {metadata['size'] / 1024:.2f} KB  \n"
            f"**Token Count:** {metadata['token_count']}"
        )
        
        st.subheader("Estimated Cost")
        estimated_cost = cost_tracker.calculate_cost(st.session_state.metadata['token_count'])
        st.success(f"Estimated cost for this analysis: **${estimated_cost:.4f}**")
    else:
        st.info("Upload a document to see details and cost estimation.")

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

if analyze_button and st.session_state.processed_text:
    content_input = st.session_state.processed_text
    estimated_cost = cost_tracker.calculate_cost(st.session_state.metadata['token_count'])

    if not cost_tracker.can_afford(estimated_cost):
        st.error(f"Analysis cannot be performed. Remaining daily budget: ${cost_tracker.get_remaining_daily_budget():.2f}, Monthly budget: ${cost_tracker.get_remaining_monthly_budget():.2f}. Estimated cost: ${estimated_cost:.2f}")
        st.stop()

    try:
        analyser = ContentAnalyser()
    except ValueError as e:
        st.error(e)
        st.stop()

    with st.spinner(f"Analyzing content with {analysis_type} analysis..."): 
        analysis = analyser.analyze_content(content_input, analysis_type)
        cost_tracker.record_usage(estimated_cost)
        
        st.divider()
        st.subheader("Analysis Results")

        if "error" in analysis:
            st.error(analysis["error"])
        else:
            st.success("Analysis complete!")
            display_analysis_results(analysis, analysis_type)

elif analyze_button and not st.session_state.processed_text:
    st.warning("Please upload a document to analyze.")
