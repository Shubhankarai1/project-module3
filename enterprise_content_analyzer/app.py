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
        accept_multiple_files=True
    )

    if uploaded_file:
        st.session_state.processed_documents = []
        processor = DocumentProcessor()
        for i, file in enumerate(uploaded_file):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                text, metadata = processor.process_file(tmp_file_path)
                st.session_state.processed_documents.append({
                    "id": f"doc_{i+1}",
                    "name": file.name,
                    "text": text,
                    "metadata": metadata
                })
            except Exception as e:
                st.error(f"Error processing file {file.name}: {e}. Skipping this file.")
            finally:
                os.remove(tmp_file_path)
        
        if st.session_state.processed_documents:
            # For displaying estimated cost, use the first document's token count as a proxy or sum them up.
            # For now, let's just show the first document's details.
            st.session_state.processed_text = st.session_state.processed_documents[0]["text"]
            st.session_state.metadata = st.session_state.processed_documents[0]["metadata"]
        else:
            st.session_state.processed_text = None
            st.session_state.metadata = None

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

if analyze_button and st.session_state.get('processed_documents'):
    total_estimated_cost = sum(cost_tracker.calculate_cost(doc['metadata']['token_count']) for doc in st.session_state.processed_documents)

    if not cost_tracker.can_afford(total_estimated_cost):
        st.error(f"Analysis cannot be performed. Remaining daily budget: ${cost_tracker.get_remaining_daily_budget():.2f}, Monthly budget: ${cost_tracker.get_remaining_monthly_budget():.2f}. Total estimated cost: ${total_estimated_cost:.2f}")
        st.stop()

    try:
        analyser = ContentAnalyser()
    except ValueError as e:
        st.error(e)
        st.stop()

    st.divider()
    st.subheader("Analysis Results")
    
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    def update_progress(current, total):
        progress_percentage = (current / total) 
        my_bar.progress(progress_percentage, text=f"Analyzing document {current} of {total}...")

    batch_results = analyser.batch_analyze(st.session_state.processed_documents, analysis_type, update_progress)
    
    my_bar.empty() # Clear the progress bar after completion

    total_actual_cost = 0
    for result in batch_results:
        doc_id = result.get("id", "N/A")
        doc_name = next((doc['name'] for doc in st.session_state.processed_documents if doc.get('id') == doc_id), f"Document {doc_id}")
        timestamp = result.get("timestamp", "N/A")

        st.markdown(f"#### Results for {doc_name} (ID: {doc_id}) at {timestamp}")
        if "error" in result:
            st.error(f"Error analyzing {doc_name}: {result['error']}")
        else:
            st.success(f"Analysis complete for {doc_name}!")
            display_analysis_results(result["analysis"], analysis_type)
            # Assuming cost is calculated per document and returned or can be re-calculated
            # For simplicity, let's re-calculate based on original token count if analysis was successful
            original_doc = next((doc for doc in st.session_state.processed_documents if doc.get('id') == doc_id), None)
            if original_doc:
                doc_cost = cost_tracker.calculate_cost(original_doc['metadata']['token_count'])
                total_actual_cost += doc_cost
        st.markdown("---") # Separator for each document's results
    
    cost_tracker.record_usage(total_actual_cost)
    st.success(f"Batch analysis complete! Total cost recorded: ${total_actual_cost:.4f}")

elif analyze_button and not st.session_state.get('processed_documents'):
    st.warning("Please upload one or more documents to analyze.")
