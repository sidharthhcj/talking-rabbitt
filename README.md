# 🐰 Talking Rabbitt - Conversational Intelligence Layer

## 🚀 The AI Product Manager Challenge

This repository contains the comprehensive deliverables for the Talking Rabbitt AI Product Manager challenge. Talking Rabbitt is a conversational intelligence layer that sits on top of enterprise data, allowing leaders to "talk" to their business in real-time.

---

## 📦 Deliverables

### 1. Functional MVP (Streamlit App)
**Location:** `app.py`

A functional web interface that demonstrates the "Magic Moment" - replacing 10-minute manual Excel filters with 5-second conversations.

**Features:**
- CSV file upload
- Natural language query interface powered by LLM
- Automated visualization generation
- Real-time data analysis

**Run locally:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

### 2. Strategy Research Documents

#### Market & Competitor Research
- **Benchmarking:** Analysis of Darwinbox, HROne, and other industry giants
- **Market Positioning:** Where Talking Rabbitt sits vs. incumbents
- **Kill Strategy:** How to defeat competitors in head-to-head sales

#### ICP & PMF Exercise
- **PMF Analysis:** Identifying burning pain points that dashboards (PowerBI/Tableau) miss
- **Ideal Customer Profile:** Specific target segment
- **Buyer Persona:** Top 5 companies, objections (Security, Data accuracy, Cost)

#### Feature Recommendations
- 3 high-impact features with RICE/MoSCoW prioritization
- Product roadmap

---

### 3. Custom Proposal
- **1-Page Executive Proposal** for a real-world company
- Specific problems Talking Rabbitt solves

---

### 4. Strategy Pitch Deck
- Comprehensive PPT covering all research, ICP, benchmarking, and roadmap

---

## 🎯 Core Value Proposition

| Traditional Approach | Talking Rabbitt |
|---------------------|-----------------|
| Open Excel/Tableau | Open app |
| Filter & select dimensions | Ask a question |
| 10 minutes of work | 5 seconds |
| Manual charts | Auto-generated visualizations |

**The Magic Moment:** When a user realizes they can get insights in 5 seconds that used to take 10 minutes.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas
- **AI/ML:** OpenAI GPT-3.5
- **Visualization:** Plotly

---

## 📊 Sample Data

Located in `sample_sales_data.csv` - includes:
- Region (North, South, East, West)
- Quarter (Q1-Q4)
- Product (Electronics, Furniture)
- Category (Tech, Home)
- Revenue ($)
- Units Sold

---

## 🔧 Configuration

### OpenAI API Key Setup
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Enter it in the sidebar of the Streamlit app
3. Enable AI-powered conversational queries

---

## 📈 Evaluation Criteria (100 Points)

| Category | Focus Area | Weight |
|----------|------------|--------|
| Market Intelligence | Benchmarking accuracy & positioning | 25% |
| ICP & Strategy | Persona depth & Kill Strategy | 25% |
| Product Prioritization | Feature logic & roadmap | 25% |
| MVP & Execution | Core value demonstration | 25% |

---

## 🏆 Success Metrics

- **User Query Time:** From 10 minutes → 5 seconds
- **Learning Curve:** Near zero - natural language only
- **Visualization Speed:** Auto-generated based on query context
- **Data Sources:** CSV upload → instant insights

---

## 📝 License

This is a demonstration project for the AI Product Manager challenge.

---

**🐰 Talking Rabbitt: Data should be a conversation, not a chore.**

