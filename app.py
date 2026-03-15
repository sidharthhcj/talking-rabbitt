"""
Talking Rabbitt - Conversational Intelligence Layer
MVP: Functional prototype demonstrating the "Magic Moment"
Powered by Groq (Free API)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

# ─────────────────────────────────────────
# CONFIG — Only the developer touches this
# ─────────────────────────────────────────

GROQ_API_KEY = "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"   # 🔑 Paste your Groq API key here
GROQ_MODEL   = "llama-3.3-70b-versatile"           # Free & powerful model on Groq

# ─────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Talking Rabbitt",
    page_icon="🐰",
    layout="wide",
)

# Session state
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def get_column_info(df):
    info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        null_count = df[col].isnull().sum()
        info.append(f"{col} ({dtype}) — {unique_count} unique values, {null_count} nulls")
    return "\n".join(info)


def generate_answer_with_groq(df, question):
    """Call Groq API to answer a question about the dataframe."""
    try:
        client = Groq(api_key=GROQ_API_KEY)

        column_info = get_column_info(df)
        data_sample = df.head(10).to_string()
        full_data   = df.to_string()

        prompt = f"""You are Talking Rabbitt, an AI analyst embedded in a business intelligence tool.
A business user has uploaded a dataset and asked a question. Answer clearly, concisely, and in plain English.
No jargon. No code. Just insights a manager can act on.

Dataset columns:
{column_info}

Sample data (first 10 rows):
{data_sample}

Full data:
{full_data}

User's question:
{question}

Give a direct, friendly answer in 2-4 sentences. Include the key number or insight upfront.
"""

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )

        return response.choices[0].message.content

    except Exception as e:
        error = str(e)
        if "401" in error or "invalid_api_key" in error.lower():
            return "❌ Invalid API key. Please check GROQ_API_KEY in app.py."
        elif "429" in error:
            return "⚠️ Rate limit hit. Wait a few seconds and try again."
        else:
            return f"❌ Something went wrong: {error}"


def determine_visualization(df, question):
    """Decide which chart type fits the question best."""
    q = question.lower()

    if any(w in q for w in ["region", "compare", "vs", "versus", "best", "top", "highest", "lowest"]):
        if "Region" in df.columns:
            return "bar_region"

    if any(w in q for w in ["trend", "time", "quarter", "month", "over", "growth", "q1", "q2", "q3", "q4"]):
        if "Quarter" in df.columns:
            return "line_quarter"

    if any(w in q for w in ["category", "split", "breakdown", "share", "portion", "pie"]):
        if "Category" in df.columns:
            return "pie_category"

    if any(w in q for w in ["product", "item"]):
        if "Product" in df.columns:
            return "bar_product"

    return None


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────

def main():

    # ── Sidebar (clean — no API key exposed to users) ──
    with st.sidebar:
        st.markdown("## 🐰 Talking Rabbitt")
        st.markdown("*Your data, in plain English.*")
        st.divider()

        st.markdown("### How it works")
        st.markdown("""
1. **Upload** your CSV file
2. **Ask** any question in plain English
3. **Get** instant answers + charts
        """)

        st.divider()

        if st.button("▶ Try with sample data", use_container_width=True):
            st.session_state.df = pd.DataFrame({
                "Region":     ["North", "South", "East", "West"] * 4,
                "Quarter":    ["Q1", "Q1", "Q1", "Q1",
                               "Q2", "Q2", "Q2", "Q2",
                               "Q3", "Q3", "Q3", "Q3",
                               "Q4", "Q4", "Q4", "Q4"],
                "Product":    ["Electronics", "Electronics", "Furniture", "Furniture"] * 4,
                "Category":   ["Tech", "Tech", "Home", "Home"] * 4,
                "Revenue":    [
                    45000, 38000, 52000, 41000,
                    48000, 42000, 55000, 44000,
                    51000, 46000, 58000, 47000,
                    54000, 49000, 60000, 50000
                ],
                "Units_Sold": [
                    150, 120, 200, 160,
                    160, 140, 210, 170,
                    170, 150, 220, 180,
                    180, 160, 230, 190
                ]
            })
            st.success("Sample data loaded! Ask away ↓")

        st.divider()

        if st.session_state.df is not None:
            df = st.session_state.df
            st.markdown("### Your data")
            col1, col2 = st.columns(2)
            col1.metric("Rows", len(df))
            col2.metric("Columns", len(df.columns))
            if "Revenue" in df.columns:
                st.metric("Total Revenue", f"${df['Revenue'].sum():,.0f}")
            if "Region" in df.columns:
                st.metric("Regions", df["Region"].nunique())


    # ── Main Content ──
    st.title("🐰 Talking Rabbitt")
    st.subheader("Ask your data anything — in plain English")

    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"],
        help="Upload any CSV with business data — sales, HR, finance, etc."
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows, {len(df.columns)} columns")

    if st.session_state.df is not None:
        df = st.session_state.df

        with st.expander("👀 Preview your data", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)

        st.divider()

        st.markdown("#### 💡 Try asking:")
        suggestions = [
            "Which region had the highest revenue?",
            "Show me the revenue trend by quarter",
            "What is the best performing category?",
            "How many units were sold in total?",
            "Compare revenue across all regions",
        ]

        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            if cols[i].button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion

        st.markdown("#### 🎙️ Or ask your own question:")
        question = st.text_input(
            label="Ask a question",
            placeholder="e.g. Which quarter had the lowest sales in the South?",
            label_visibility="collapsed",
            key="question_input"
        )

        if "pending_question" in st.session_state:
            question = st.session_state.pending_question
            del st.session_state.pending_question

        if st.button("Ask Rabbitt 🐰", type="primary") and question:
            with st.spinner("Rabbitt is thinking..."):
                answer = generate_answer_with_groq(df, question)
                viz    = determine_visualization(df, question)
                st.session_state.chat_history.append({
                    "q": question,
                    "a": answer,
                    "viz": viz
                })

        if st.session_state.chat_history:
            st.divider()
            st.markdown("### Conversation")

            for chat in reversed(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(chat["q"])

                with st.chat_message("assistant", avatar="🐰"):
                    st.write(chat["a"])

                    viz = chat["viz"]

                    if viz == "bar_region" and "Region" in df.columns and "Revenue" in df.columns:
                        fig = px.bar(
                            df.groupby("Region")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False),
                            x="Region", y="Revenue",
                            title="Revenue by Region",
                            color="Revenue",
                            color_continuous_scale="Blues"
                        )
                        fig.update_layout(showlegend=False, coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)

                    elif viz == "line_quarter" and "Quarter" in df.columns and "Revenue" in df.columns:
                        fig = px.line(
                            df.groupby("Quarter")["Revenue"].sum().reset_index(),
                            x="Quarter", y="Revenue",
                            title="Revenue Trend by Quarter",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    elif viz == "pie_category" and "Category" in df.columns and "Revenue" in df.columns:
                        fig = px.pie(
                            df.groupby("Category")["Revenue"].sum().reset_index(),
                            names="Category", values="Revenue",
                            title="Revenue by Category"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    elif viz == "bar_product" and "Product" in df.columns and "Revenue" in df.columns:
                        fig = px.bar(
                            df.groupby("Product")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False),
                            x="Product", y="Revenue",
                            title="Revenue by Product"
                        )
                        st.plotly_chart(fig, use_container_width=True)

            if st.button("🗑️ Clear conversation"):
                st.session_state.chat_history = []
                st.rerun()

    else:
        st.info("👆 Upload a CSV file above, or click **▶ Try with sample data** in the sidebar to get started.")


if __name__ == "__main__":
    main()
