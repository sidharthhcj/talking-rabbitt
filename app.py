"""
Talking Rabbitt - Conversational Intelligence Layer
MVP: Functional prototype demonstrating the "Magic Moment"

This Streamlit app allows users to:
1. Upload a CSV file (sales data)
2. Ask natural language questions about their data
3. Get instant text answers powered by LLM
4. See automated visualizations based on their queries

The "Magic Moment": Replacing 10-minute manual Excel filters with 5-second conversations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import openai
import os
from io import StringIO
import re

# Page Configuration
st.set_page_config(
    page_title="Talking Rabbitt - AI Product Manager",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 24px;
        color: #4ECDC4;
        margin-bottom: 30px;
    }
    .magic-moment {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stat-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = None


def get_column_info(df):
    """Get information about DataFrame columns for LLM context."""
    info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        sample_values = df[col].dropna().head(3).tolist()
        info.append(f"- {col}: {dtype}, {null_count} nulls, {unique_count} unique values, samples: {sample_values}")
    return "\n".join(info)


def generate_answer_with_llm(df, question, api_key):
    """Generate answer using OpenAI LLM."""
    if not api_key:
        return "Please enter your OpenAI API key in the sidebar to enable AI-powered queries."
    
    try:
        openai.api_key = api_key
        
        # Get data summary
        column_info = get_column_info(df)
        data_sample = df.head(10).to_string()
        
        prompt = f"""You are Talking Rabbitt, an AI analytics assistant. You help users understand their data through conversation.

DataFrame Columns:
{column_info}

Data Sample (first 10 rows):
{data_sample}

User Question: {question}

Instructions:
1. Analyze the data to answer the user's question accurately
2. Provide a clear, concise text answer
3. If the question requires a specific calculation or aggregation, perform it
4. Keep your answer brief but informative
5. If the question asks about visualizations, mention what chart would be helpful

Respond with just the answer to the question:"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please check your API key and try again."


def determine_visualization(df, question):
    """Determine what visualization to create based on the question."""
    question_lower = question.lower()
    
    # Revenue/Sales by Region
    if 'region' in question_lower and ('revenue' in question_lower or 'sales' in question_lower or 'highest' in question_lower or 'lowest' in question_lower):
        if 'Region' in df.columns and 'Revenue' in df.columns:
            return 'bar', {'x': 'Region', 'y': 'Revenue', 'title': 'Revenue by Region'}
        elif 'Region' in df.columns and 'Sales' in df.columns:
            return 'bar', {'x': 'Region', 'y': 'Sales', 'title': 'Sales by Region'}
    
    # Revenue/Sales over Time
    if 'time' in question_lower or 'trend' in question_lower or 'quarter' in question_lower or 'month' in question_lower or 'year' in question_lower:
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower() or 'quarter' in col.lower() or 'month' in col.lower():
                date_col = col
                break
        
        revenue_col = None
        for col in df.columns:
            if 'revenue' in col.lower() or 'sales' in col.lower() or 'amount' in col.lower():
                revenue_col = col
                break
        
        if date_col and revenue_col:
            return 'line', {'x': date_col, 'y': revenue_col, 'title': f'{revenue_col} Over Time'}
    
    # Category/Product breakdown
    if 'category' in question_lower or 'product' in question_lower:
        if 'Category' in df.columns and 'Revenue' in df.columns:
            return 'pie', {'names': 'Category', 'values': 'Revenue', 'title': 'Revenue by Category'}
        elif 'Product' in df.columns and 'Revenue' in df.columns:
            return 'pie', {'names': 'Product', 'values': 'Revenue', 'title': 'Revenue by Product'}
    
    # Top performers
    if 'top' in question_lower:
        if 'Region' in df.columns and 'Revenue' in df.columns:
            top_df = df.groupby('Region')['Revenue'].sum().reset_frame().sort_values('Revenue', ascending=False).head(5)
            return 'bar', {'x': 'Region', 'y': 'Revenue', 'title': 'Top 5 Regions by Revenue'}
    
    return None, None


def create_visualization(df, viz_type, params):
    """Create Plotly visualization based on type and parameters."""
    try:
        if viz_type == 'bar':
            fig = px.bar(df, x=params['x'], y=params['y'], title=params['title'], 
                        color=params['x'], template="plotly_white")
        elif viz_type == 'line':
            fig = px.line(df, x=params['x'], y=params['y'], title=params['title'],
                         markers=True, template="plotly_white")
        elif viz_type == 'pie':
            # Aggregate for pie chart
            agg_col = params['values']
            grouped = df.groupby(params['names'])[agg_col].sum().reset_index()
            fig = px.pie(grouped, names=params['names'], values=agg_col, 
                        title=params['title'], hole=0.4)
        elif viz_type == 'scatter':
            fig = px.scatter(df, x=params['x'], y=params['y'], title=params['title'],
                           size=params.get('size', None), color=params.get('color', None))
        
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        return None


# Main Application
def main():
    # Header
    st.markdown('<p class="main-header">🐰 Talking Rabbitt</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Conversational Intelligence for Enterprise Data</p>', unsafe_allow_html=True)
    
    # Sidebar - API Key and Settings
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input("OpenAI API Key", type="password", 
                               help="Enter your OpenAI API key to enable AI-powered queries")
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key configured!")
        
        st.divider()
        
        st.markdown("### 📊 Sample Data")
        if st.button("Load Sample Sales Data"):
            # Create sample sales data
            data = {
                'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West',
                          'North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
                'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2',
                           'Q3', 'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4', 'Q4'],
                'Product': ['Electronics', 'Electronics', 'Furniture', 'Furniture',
                           'Electronics', 'Electronics', 'Furniture', 'Furniture',
                           'Electronics', 'Electronics', 'Furniture', 'Furniture',
                           'Electronics', 'Electronics', 'Furniture', 'Furniture'],
                'Category': ['Tech', 'Tech', 'Home', 'Home', 'Tech', 'Tech', 'Home', 'Home',
                            'Tech', 'Tech', 'Home', 'Home', 'Tech', 'Tech', 'Home', 'Home'],
                'Revenue': [45000, 38000, 52000, 41000, 48000, 42000, 55000, 44000,
                           51000, 46000, 58000, 47000, 54000, 49000, 60000, 50000],
                'Units_Sold': [150, 120, 200, 160, 160, 140, 210, 170,
                              170, 150, 220, 180, 180, 160, 230, 190]
            }
            st.session_state.df = pd.DataFrame(data)
            st.success("✅ Sample data loaded!")
        
        if st.session_state.df is not None:
            st.markdown(f"**Rows:** {len(st.session_state.df)}")
            st.markdown(f"**Columns:** {len(st.session_state.df.columns)}")
    
    # Main Content
    # Magic Moment Section
    st.markdown("""
    <div class="magic-moment">
        <h2>✨ The Magic Moment</h2>
        <p>Stop spending 10 minutes filtering Excel sheets. Ask a question, get an answer in 5 seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File Upload
    st.markdown("### 📁 Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Upload your sales data CSV")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Display Data Preview
    if st.session_state.df is not None:
        df = st.session_state.df
        
        with st.expander("📋 Preview Your Data"):
            st.dataframe(df.head(10), width=None)
            st.markdown("**Column Types:**")
            st.write(df.dtypes)
        
        # Conversational Query Interface
        st.markdown("### 💬 Ask Questions About Your Data")
        
        # Example questions
        st.markdown("**Try these questions:**")
        example_questions = [
            "Which region had the highest revenue?",
            "What was the total revenue in Q1?",
            "Show me the sales trend over time",
            "Which product category generates the most revenue?"
        ]
        
        cols = st.columns(2)
        for i, q in enumerate(example_questions):
            if cols[i % 2].button(f"📌 {q}", key=f"example_{i}"):
                st.session_state.current_question = q
        
        # Question input
        default_q = st.session_state.get('current_question', '')
        question = st.text_input("Ask your question:", value=default_q, 
                                placeholder="e.g., Which region had the highest revenue in Q1?",
                                key="question_input")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            ask_button = st.button("🔍 Ask Rabbitt", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear History", use_container_width=True)
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        # Process Question
        if ask_button and question:
            with st.spinner("🤔 Thinking..."):
                # Generate answer
                answer = generate_answer_with_llm(df, question, st.session_state.api_key)
                
                # Determine if visualization is needed
                viz_type, viz_params = determine_visualization(df, question)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': question,
                    'answer': answer,
                    'viz_type': viz_type,
                    'viz_params': viz_params
                })
        
        # Display Chat History
        if st.session_state.chat_history:
            st.markdown("### 📜 Conversation History")
            
            for i, chat in enumerate(st.session_state.chat_history):
                with st.container():
                    st.markdown(f"**🧑 You:** {chat['question']}")
                    st.markdown(f"**🐰 Rabbitt:** {chat['answer']}")
                    
                    # Show visualization if applicable
                    if chat['viz_type'] and chat['viz_params']:
                        try:
                            fig = create_visualization(df, chat['viz_type'], chat['viz_params'])
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Couldn't create visualization: {str(e)}")
                    
                    st.divider()
        
        # Data Statistics
        st.markdown("### 📈 Quick Stats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric(f"Sum ({numeric_cols[0]})", f"{df[numeric_cols[0]].sum():,.0f}")
            with col4:
                st.metric(f"Avg ({numeric_cols[0]})", f"{df[numeric_cols[0]].mean():,.0f}")
        
        # Auto-generate some visualizations
        st.markdown("### 📊 Auto-Visualizations")
        
        viz_tabs = st.tabs(["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
        
        with viz_tabs[0]:
            if 'Region' in df.columns and 'Revenue' in df.columns:
                fig = px.bar(df.groupby('Region')['Revenue'].sum().reset_index(), 
                           x='Region', y='Revenue', title='Revenue by Region',
                           color='Region', template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
        
        with viz_tabs[1]:
            if 'Quarter' in df.columns and 'Revenue' in df.columns:
                fig = px.line(df.groupby('Quarter')['Revenue'].sum().reset_index(),
                             x='Quarter', y='Revenue', title='Revenue by Quarter',
                             markers=True, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
        
        with viz_tabs[2]:
            if 'Category' in df.columns and 'Revenue' in df.columns:
                fig = px.pie(df.groupby('Category')['Revenue'].sum().reset_index(),
                            names='Category', values='Revenue', title='Revenue by Category',
                            hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        
        with viz_tabs[3]:
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                               title=f'{numeric_cols[0]} vs {numeric_cols[1]}',
                               template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Welcome screen when no data loaded
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Enter your OpenAI API key** in the sidebar (or skip for basic functionality)
        2. **Load sample data** or upload your own CSV
        3. **Ask questions** in natural language
        
        ### 💡 Example Use Cases
        - Sales managers asking "Which product sold best this quarter?"
        - Finance teams asking "What was our revenue by region?"
        - Executives asking "Show me the trend over the last 12 months"
        
        ### 🔑 Key Features
        - **Natural Language Queries**: Ask questions in plain English
        - **Auto-Visualizations**: Charts appear automatically based on your questions
        - **Instant Insights**: Get answers in seconds, not minutes
        """)
        
        # Demo with pre-loaded data
        st.markdown("### 🎬 Quick Demo")
        if st.button("Run Demo with Sample Data"):
            # Load sample data
            data = {
                'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
                'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2'],
                'Product': ['Electronics', 'Electronics', 'Furniture', 'Furniture',
                           'Electronics', 'Electronics', 'Furniture', 'Furniture'],
                'Category': ['Tech', 'Tech', 'Home', 'Home', 'Tech', 'Tech', 'Home', 'Home'],
                'Revenue': [45000, 38000, 52000, 41000, 48000, 42000, 55000, 44000],
                'Units_Sold': [150, 120, 200, 160, 160, 140, 210, 170]
            }
            st.session_state.df = pd.DataFrame(data)
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>🐰 Talking Rabbitt MVP | Built for the AI Product Manager Challenge</p>
        <p>Transforming data analysis from 10 minutes to 5 seconds</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

