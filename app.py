"""
Talking Rabbitt - Conversational Intelligence Layer
MVP: Functional prototype demonstrating the "Magic Moment"
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import openai

# Page Configuration
st.set_page_config(
    page_title="Talking Rabbitt - AI Product Manager",
    page_icon="🐰",
    layout="wide",
)

# Session state
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def get_column_info(df):
    info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        info.append(f"{col} ({dtype}) - {unique_count} unique values, {null_count} nulls")
    return "\n".join(info)


def generate_answer_with_llm(df, question, api_key):

    if not api_key:
        return "Please enter your OpenAI API key in the sidebar."

    try:
        openai.api_key = api_key

        column_info = get_column_info(df)
        data_sample = df.head(5).to_string()

        prompt = f"""
You are Talking Rabbitt AI.

Dataset Columns:
{column_info}

Sample Data:
{data_sample}

Question:
{question}

Answer clearly and briefly.
"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def determine_visualization(df, question):

    q = question.lower()

    if "region" in q and "revenue" in q and "Region" in df.columns:
        return "bar"

    if "trend" in q or "time" in q or "quarter" in q:
        return "line"

    if "category" in q:
        return "pie"

    return None


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────

def main():

    st.title("🐰 Talking Rabbitt")
    st.subheader("Conversational Intelligence for Enterprise Data")

    # Sidebar
    with st.sidebar:

        st.header("⚙️ Settings")

        api_key = st.text_input(
            "OpenAI API Key",
            type="password"
        )

        if api_key:
            st.session_state.api_key = api_key
            st.success("API Key Added")

        st.divider()

        if st.button("Load Sample Data"):

            data = {
                "Region": ["North", "South", "East", "West"] * 4,
                "Quarter": ["Q1", "Q2", "Q3", "Q4"] * 4,
                "Category": ["Tech", "Home", "Tech", "Home"] * 4,
                "Revenue": [
                    45000, 38000, 52000, 41000,
                    48000, 42000, 55000, 44000,
                    51000, 46000, 58000, 47000,
                    54000, 49000, 60000, 50000
                ]
            }

            st.session_state.df = pd.DataFrame(data)

            st.success("Sample data loaded")


    # Upload CSV

    st.header("Upload CSV")

    file = st.file_uploader("Upload sales CSV", type="csv")

    if file:

        df = pd.read_csv(file)
        st.session_state.df = df

        st.success(f"Loaded {len(df)} rows")


    # Show data preview

    if st.session_state.df is not None:

        df = st.session_state.df

        with st.expander("Preview Data"):

            # FIXED ERROR HERE
            st.dataframe(df.head(10), use_container_width=True)

            st.write(df.dtypes)


        st.header("Ask Questions")

        question = st.text_input(
            "Ask something about your data",
            placeholder="Which region had the highest revenue?"
        )

        if st.button("Ask Rabbitt") and question:

            with st.spinner("Rabbitt thinking..."):

                answer = generate_answer_with_llm(
                    df,
                    question,
                    st.session_state.api_key
                )

                viz = determine_visualization(df, question)

                st.session_state.chat_history.append(
                    {
                        "q": question,
                        "a": answer,
                        "viz": viz
                    }
                )


        # Show history

        for chat in st.session_state.chat_history:

            st.markdown(f"**You:** {chat['q']}")
            st.markdown(f"**Rabbitt:** {chat['a']}")

            if chat["viz"] == "bar" and "Region" in df.columns:

                fig = px.bar(
                    df.groupby("Region")["Revenue"].sum().reset_index(),
                    x="Region",
                    y="Revenue",
                    title="Revenue by Region"
                )

                st.plotly_chart(fig, use_container_width=True)

            if chat["viz"] == "line" and "Quarter" in df.columns:

                fig = px.line(
                    df.groupby("Quarter")["Revenue"].sum().reset_index(),
                    x="Quarter",
                    y="Revenue",
                    title="Revenue Trend"
                )

                st.plotly_chart(fig, use_container_width=True)

            if chat["viz"] == "pie" and "Category" in df.columns:

                fig = px.pie(
                    df.groupby("Category")["Revenue"].sum().reset_index(),
                    names="Category",
                    values="Revenue"
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()


    else:

        st.info("Upload a CSV file or load sample data to begin.")


if __name__ == "__main__":
    main()
