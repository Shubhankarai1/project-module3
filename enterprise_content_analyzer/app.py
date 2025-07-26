import streamlit as st
import pandas as pd
from content_analyzer.analyzer import ContentAnalyser
from content_analyzer.document_processor import DocumentProcessor
from content_analyzer.cost_tracker import CostTracker
import os
import tempfile
import json
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Enterprise Content Analysis Report")

# Initialize session state
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None
if 'batch_results_df' not in st.session_state:
    st.session_state.batch_results_df = pd.DataFrame()

# Initialize CostTracker
cost_tracker = CostTracker()

# Display remaining budget in the sidebar
st.sidebar.subheader("Budget Information")
st.sidebar.write(f"Daily Remaining: **${cost_tracker.get_remaining_daily_budget():.2f}**")
st.sidebar.write(f"Monthly Remaining: **${cost_tracker.get_remaining_monthly_budget():.2f}**")

# Tabs for Single Analysis and Batch Processing
tab1, tab2, tab3 = st.tabs(["Single Analysis", "Batch Processing", "Analytics"])

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

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("Select the analysis type and upload your document below.")
        single_analysis_type = st.selectbox(
            "Analysis Type (Single Document)",
            ("General Business", "Competitive Intelligence", "Customer Feedback"),
            key="single_analysis_type"
        )
        
        single_uploaded_file = st.file_uploader(
            "Upload a single document to analyze",
            type=["txt", "pdf", "docx"],
            key="single_file_uploader"
        )

        if single_uploaded_file:
            processor = DocumentProcessor()
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(single_uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(single_uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                text, metadata = processor.process_file(tmp_file_path)
                st.session_state.processed_text = text
                st.session_state.metadata = metadata
            except Exception as e:
                st.error(f"Error processing file {single_uploaded_file.name}: {e}")
                st.session_state.processed_text = None
                st.session_state.metadata = None
            finally:
                os.remove(tmp_file_path)
        else:
            st.session_state.processed_text = None
            st.session_state.metadata = None

        single_analyze_button = st.button("Analyse Single Document")

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

    if single_analyze_button and st.session_state.get('processed_text'):
        estimated_cost = cost_tracker.calculate_cost(st.session_state.metadata['token_count'])
        if not cost_tracker.can_afford(estimated_cost):
            st.error(f"Analysis cannot be performed. Remaining daily budget: ${cost_tracker.get_remaining_daily_budget():.2f}, Monthly budget: ${cost_tracker.get_remaining_monthly_budget():.2f}. Total estimated cost: ${total_estimated_cost:.2f}")
            st.stop()

        try:
            analyser = ContentAnalyser()
            with st.spinner("Analyzing document..."):
                analysis_result = analyser.analyze_content(st.session_state.processed_text, single_analysis_type)
            
            if "error" in analysis_result:
                st.error(f"Analysis failed: {analysis_result['error']}")
            else:
                st.divider()
                display_analysis_results(analysis_result, single_analysis_type)
                cost_tracker.record_usage(estimated_cost)
                st.success(f"Analysis complete! Cost recorded: ${estimated_cost:.4f}")
        except ValueError as e:
            st.error(e)
        except Exception as e:
            st.error(f"An unexpected error occurred during analysis: {e}")
    elif single_analyze_button and not st.session_state.get('processed_text'):
        st.warning("Please upload a document to analyze.")

with tab2:
    st.write("Select the analysis type and upload multiple documents for batch processing.")
    batch_analysis_type = st.selectbox(
        "Analysis Type (Batch Processing)",
        ("General Business", "Competitive Intelligence", "Customer Feedback"),
        key="batch_analysis_type"
    )
    
    batch_uploaded_files = st.file_uploader(
        "Upload multiple documents to analyze",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
        key="batch_file_uploader"
    )

    batch_analyze_button = st.button("Analyse Batch Documents")

    if batch_analyze_button and batch_uploaded_files:
        st.session_state.processed_documents = []
        processor = DocumentProcessor()
        for i, file in enumerate(batch_uploaded_files):
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
            st.subheader("Batch Analysis Results")
            
            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)

            def update_progress(current, total):
                progress_percentage = (current / total) 
                my_bar.progress(progress_percentage, text=f"Analyzing document {current} of {total}...")

            batch_results = analyser.batch_analyze(st.session_state.processed_documents, batch_analysis_type, update_progress)
            
            my_bar.empty() # Clear the progress bar after completion

            results_data = []
            total_actual_cost = 0
            total_confidence = 0
            analyzed_docs_count = 0

            for result in batch_results:
                doc_id = result.get("id", "N/A")
                doc_name = next((doc['name'] for doc in st.session_state.processed_documents if doc.get('id') == doc_id), f"Document {doc_id}")
                
                if "error" in result:
                    st.error(f"Error analyzing {doc_name}: {result['error']}")
                    results_data.append({
                        "Document": doc_name,
                        "Type": "N/A",
                        "Sentiment": "Error",
                        "Business Impact": "N/A",
                        "Confidence": "N/A",
                        "Cost": 0
                    })
                else:
                    analysis = result["analysis"]
                    doc_type = next((doc['metadata']['type'] for doc in st.session_state.processed_documents if doc.get('id') == doc_id), "N/A")
                    
                    sentiment = analysis.get("sentiment_analysis", {}).get("overall_sentiment", analysis.get("sentiment_analysis", {}).get("sentiment", "N/A"))
                    confidence = analysis.get("sentiment_analysis", {}).get("confidence_score", "N/A")
                    business_impact = analysis.get("business_impact", "N/A")

                    original_doc = next((doc for doc in st.session_state.processed_documents if doc.get('id') == doc_id), None)
                    doc_cost = 0
                    if original_doc:
                        doc_cost = cost_tracker.calculate_cost(original_doc['metadata']['token_count'])
                        total_actual_cost += doc_cost
                    
                    results_data.append({
                        "Document": doc_name,
                        "Type": doc_type,
                        "Sentiment": sentiment,
                        "Business Impact": business_impact,
                        "Confidence": confidence,
                        "Cost": doc_cost
                    })
                    
                    if isinstance(confidence, (int, float)):
                        total_confidence += confidence
                        analyzed_docs_count += 1

            st.session_state.batch_results_df = pd.DataFrame(results_data)
            st.dataframe(st.session_state.batch_results_df)

            col_metrics1, col_metrics2 = st.columns(2)
            with col_metrics1:
                st.metric(label="Total Cost", value=f"${total_actual_cost:.4f}")
            with col_metrics2:
                avg_confidence = (total_confidence / analyzed_docs_count) if analyzed_docs_count > 0 else 0
                st.metric(label="Average Confidence", value=f"{avg_confidence:.2f}")

            csv = st.session_state.batch_results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="batch_analysis_results.csv",
                mime="text/csv",
            )
            
            cost_tracker.record_usage(total_actual_cost)
            st.success(f"Batch analysis complete! Total cost recorded: ${total_actual_cost:.4f}")
        else:
            st.warning("No documents were successfully processed for batch analysis.")
    elif batch_analyze_button and not batch_uploaded_files:
        st.warning("Please upload one or more documents for batch analysis.")

with tab3:
    st.subheader("Analysis Dashboard")
    if not st.session_state.batch_results_df.empty:
        df = st.session_state.batch_results_df.copy()
        
        # Sentiment distribution pie chart
        st.markdown("#### Sentiment Distribution")
        sentiment_counts = df['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_counts, values='Count', names='Sentiment', title='Distribution of Sentiments')
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # Business impact Bar chart
        st.markdown("#### Business Impact Breakdown")
        business_impact_counts = df['Business Impact'].value_counts().reset_index()
        business_impact_counts.columns = ['Business Impact', 'Count']
        fig_impact = px.bar(business_impact_counts, x='Business Impact', y='Count', title='Business Impact Breakdown')
        st.plotly_chart(fig_impact, use_container_width=True)

        # Confidence score histogram
        st.markdown("#### Confidence Score Distribution")
        # Filter out non-numeric confidence scores
        numeric_confidence = pd.to_numeric(df['Confidence'], errors='coerce').dropna()
        if not numeric_confidence.empty:
            fig_confidence = px.histogram(numeric_confidence, nbins=10, title='Distribution of Confidence Scores')
            st.plotly_chart(fig_confidence, use_container_width=True)
        else:
            st.info("No numeric confidence scores available for histogram.")

        # Cost per document analysis
        st.markdown("#### Cost Per Document")
        fig_cost = px.bar(df, x='Document', y='Cost', title='Cost Per Document Analysis')
        st.plotly_chart(fig_cost, use_container_width=True)

        # Content type breakdown
        st.markdown("#### Content Type Breakdown")
        content_type_counts = df['Type'].value_counts().reset_index()
        content_type_counts.columns = ['Type', 'Count']
        fig_type = px.pie(content_type_counts, values='Count', names='Type', title='Breakdown of Content Types')
        st.plotly_chart(fig_type, use_container_width=True)

    else:
        st.info("Run a batch analysis to see analytics.")
