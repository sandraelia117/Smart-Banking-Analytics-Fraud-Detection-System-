# 🏦 Smart Banking Analytics & Fraud Detection System

An end-to-end **Data Engineering + Data Warehouse + Business Intelligence + Machine Learning + Generative AI** project that simulates a real-world banking analytics platform capable of processing transactions, detecting fraud, and answering natural-language questions about the data.

---

## 📌 Overview

Banks process thousands of transactions every day, making manual fraud detection impossible. This project builds a complete pipeline — from raw CSV data to a production-style Streamlit application — that provides:

- 📊 **Analytics Dashboard** for banking KPIs and trends
- 🚨 **Fraud Detection Engine** combining Machine Learning and business rules
- 🤖 **AI Banking Assistant** that answers questions in natural language using LLMs

---

## 🧱 Project Architecture

```
                 CSV DATA
                    |
                    ↓
                 ETL Pipeline
              (Python + Pandas)
                    |
                    ↓
          PostgreSQL Database
                 (OLTP)
                    |
                    ↓
          Data Warehouse
             Star Schema
                    |
        -----------------------
        |                     |
 BI Dashboard          ML Fraud Model
 (Streamlit)          (Scikit-learn)
        |                     |
        -------- AI Assistant --------
              Gemini / Groq
```

---

## 🚀 Project Phases

### 1. Business Understanding & Requirement Analysis
Defined the business problem (manual fraud detection at scale) and the required solution: Analytics, Fraud Detection, and an AI Assistant.
**Tools:** Word/Google Docs, Draw.io, Notion

### 2. Data Collection
Collected raw banking datasets: `Customers`, `Accounts`, `Transactions`, `Branches`, `Employees`, `Loans`, `CreditCards`, `ATMs`, `Beneficiaries`, `MobileBanking`.
**Tools:** Excel, CSV, Python (Pandas, NumPy)

### 3. Data Exploration (EDA)
Explored the data — record counts, missing values, duplicates, data types, and transaction distributions.
**Tools:** Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook

### 4. Database Design (OLTP)
Designed an ERD and built the relational schema for the `Banking_System_DB`.
**Tools:** Draw.io, Lucidchart, PostgreSQL, SQLAlchemy, psycopg2

### 5. ETL Pipeline
Built an Extract → Transform → Load pipeline to clean and load CSV data into PostgreSQL.
**Tools:** Pandas, SQLAlchemy, Python

### 6. Data Warehouse Design (Star Schema)
Designed a dimensional model for fast analytics:
- **Fact Table:** `FACT_TRANSACTIONS`
- **Dimension Tables:** `DIM_CUSTOMER`, `DIM_ACCOUNT`, `DIM_TIME`, `DIM_BRANCH`, `DIM_CHANNEL`

**Tools:** PostgreSQL, SQL, Draw.io

### 7. Data Warehouse ETL
Migrated data from the OLTP database into the Data Warehouse.
**Tools:** Python, SQL, Pandas

### 8. Business Intelligence Dashboard
Built an executive dashboard with KPIs (customers, accounts, balances, fraud cases) and visual analytics (channel trends, monthly trends, fraud distribution).
**Tools:** Streamlit, Plotly, Matplotlib, PostgreSQL

### 9–11. Fraud Detection: Feature Engineering & Preprocessing
Engineered features such as transaction amount, frequency, failed attempts, time-since-last-transaction, night transactions, and new ATM usage. Applied Label Encoding, One-Hot Encoding, and Scaling.
**Tools:** Pandas, Scikit-learn

### 12. Machine Learning Model
Trained a **Random Forest Classifier** on historical transactions and saved the model as `fraud_model.pkl`.
**Tools:** Scikit-learn, Pickle, Python

### 13. Rule-Based Fraud Engine
Added explicit banking rules (e.g., amount > 50,000, night transaction, new ATM, multiple failed attempts).
**Tools:** Python

### 14. Hybrid Risk Scoring
Combined ML prediction score + rule-based score into a Final Risk Score, categorized as **Low / Medium / Critical Risk**.

### 15. Explainable AI
Displays the reasons behind each risk decision (e.g., large amount, night transaction, new device).
**Tools:** Python, Rule Engine

### 16. AI Banking Assistant
A natural-language assistant that converts user questions into SQL, executes them safely, and returns answers.
**Tools:** Gemini API, Groq API, LangChain, SQL Validation (Read-Only Queries)

### 17. Streamlit Application
Structured app with:
```
app.py
components/
utils/
models/
data/
```
**Pages:** Dashboard · Fraud Detection · AI Assistant (Chat)

### 18. Security
- Environment variables (`.env`)
- API key & database password protection
- SQL injection prevention
- Read-only AI queries

**Tools:** python-dotenv, PostgreSQL Security

### 19. Testing
- Database testing (Insert/Update/Delete)
- ML testing (Accuracy, Precision, Recall, F1-score)

**Tools:** Pytest, Scikit-learn Metrics

### 20. Deployment
Deployed via **Streamlit Cloud** or **Docker**, with version control on **GitHub**.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Programming | Python |
| Database | PostgreSQL |
| ETL | Pandas + SQLAlchemy |
| Data Warehouse | PostgreSQL (Star Schema) |
| Visualization | Streamlit + Plotly |
| Machine Learning | Scikit-learn (Random Forest) |
| AI Assistant | Gemini / Groq + LangChain |
| Documentation | README + Draw.io |
| Version Control | Git + GitHub |
| Deployment | Streamlit Cloud / Docker |

---

## 📂 Repository Structure

```
smart-banking-analytics/
├── app.py
├── components/
├── utils/
├── models/
│   └── fraud_model.pkl
├── data/
│   ├── Customers.csv
│   ├── Accounts.csv
│   ├── Transactions.csv
│   ├── Branches.csv
│   ├── Employees.csv
│   ├── Loans.csv
│   ├── CreditCards.csv
│   ├── ATMs.csv
│   ├── Beneficiaries.csv
│   └── MobileBanking.csv
├── etl/
├── notebooks/
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/<your-username>/smart-banking-analytics.git
   cd smart-banking-analytics
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file (database credentials, Gemini/Groq API keys)
4. Run the ETL pipeline to populate PostgreSQL
5. Launch the app
   ```bash
   streamlit run app.py
   ```

---

## ✅ Skills Demonstrated

## 👥 🧱 Team Roles & contributions


👩‍💻 Sandra Elia Attia Ibrahim – Team Lead | Data Engineering & AI Developer

Designed and implemented the complete Python application using Streamlit.
Developed the Executive Dashboard, Fraud Detection workflow, and AI Banking Assistant.
Built the Machine Learning fraud detection model and integrated the AI features (Gemini/Groq).
Designed and created the PostgreSQL Operational Database.
Designed and implemented the Data Warehouse tables (Star Schema).
Performed data analysis and implemented the fraud analytics logic.
Integrated all project modules into one end-to-end banking system.
https://github.com/sandraelia117


👩‍💻 Salma – ETL Engineer

Developed the ETL Pipeline (Extract, Transform, Load).
Extracted data from CSV files, transformed and cleaned the datasets.
Loaded the processed data into the Data Warehouse.
https://github.com/salmakelany

👨‍💻 Mostafa – Database Designer

Designed the Entity Relationship Diagram (ERD).
Designed the Data Warehouse architecture and Star Schema documentation.
https://github.com/mostafatzakii-hue


👨‍💻 Abdelrahman – BI Dashboard Developer

Designed and developed the Business Intelligence Dashboard for data visualization and reporting.
https://github.com/1sa3dany

👨‍💻 Mohamed – Presentation & Documentation

Prepared the project presentation and presentation materials for the final project demonstration.

Data Engineering · ETL Development · Database Design · Data Warehousing · Star Schema Modeling · Business Intelligence · Machine Learning · Generative AI Integration

---

## 🏷️ Tags

`#DataEngineering` `#DataScience` `#MachineLearning` `#ArtificialIntelligence` `#GenerativeAI` `#DataWarehouse` `#ETL` `#PostgreSQL` `#Python` `#Streamlit` `#BusinessIntelligence` `#FraudDetection` `#Analytics`
