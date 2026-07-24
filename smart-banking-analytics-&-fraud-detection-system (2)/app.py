"""
app.py
------
Smart Banking Analytics & Fraud Detection System
Main Entry Point (Single-File Version — all pages merged into one code file).

Run:
    streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st

from utils.db import (
    run_query,
    get_dashboard_statistics,
    get_transaction_by_id,
    get_customer_profile,
    validate_readonly_sql,
)
from utils.feature_engineering import compute_context_features
from utils.fraud_rules import build_fraud_rules, build_explanations
from models.model_loader import load_model_bundle, predict_fraud

from components.summary_cards import render_kpi_cards, render_today_stats
from components.transaction_form import render_transaction_form
from components.transaction_preview import render_transaction_preview
from components.transaction_details import render_saved_transaction_details
from components.fraud_dashboard import render_fraud_dashboard_metrics
from components.customer_profile import render_customer_profile_card
from components.timeline import render_customer_timeline
from components.similar_cases import render_similar_cases_table
from components.feature_importance import render_feature_importance_chart
from components.recommended_actions import render_recommended_actions


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Smart Banking Analytics & Fraud Detection",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS styles
styles_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(styles_path):
    with open(styles_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Initialize Session State
# ----------------------------------------------------------------------
if "pending_transaction" not in st.session_state:
    st.session_state.pending_transaction = None

if "confirmed_transaction" not in st.session_state:
    st.session_state.confirmed_transaction = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None


# ============================================================================
# PAGE 1: EXECUTIVE DASHBOARD
# ============================================================================
def render_dashboard_page():
    st.title("📊 Banking Analytics Executive Dashboard")
    st.caption("Live high-level overview of core banking metrics, transactions, and fraud distribution.")

    try:
        kpis = get_dashboard_statistics()
        render_kpi_cards(kpis)

        st.divider()

        st.subheader("📋 Recent Transactions (Linked with ATM & Employee)")
        recent = run_query(
            """
            SELECT
                t.transactionid, t.accountid, t.transactiondate, t.transactiontype,
                t.amount, t.channel, t.status, t.isfraud,
                a.location AS atm_location,
                CONCAT(e.firstname, ' ', e.lastname) AS employee_name
            FROM transactions t
            LEFT JOIN atms a ON t.atmid = a.atmid
            LEFT JOIN employees e ON t.employeeid = e.employeeid
            ORDER BY t.transactiondate DESC LIMIT 20;
            """
        )
        if not recent.empty:
            st.dataframe(recent, use_container_width=True)
        else:
            st.info("No transaction records found in database.")

        st.divider()

        st.subheader("📈 Transactions Volume by Channel")
        by_channel = run_query(
            """
            SELECT channel, COUNT(*) AS txn_count, COALESCE(SUM(amount), 0) AS total_amount
            FROM transactions
            GROUP BY channel
            ORDER BY txn_count DESC;
            """
        )
        if not by_channel.empty:
            st.bar_chart(by_channel.set_index("channel")["txn_count"])
        else:
            st.info("No channel data available.")

    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        st.info("Please verify DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD in your environment / .env file.")


# ============================================================================
# PAGE 2: FRAUD DETECTION & WORKFLOW
# ============================================================================
def render_full_analysis_sections(tx: pd.Series, analysis_res: dict, key_prefix: str = "analysis"):
    """
    Renders all fraud analysis sub-components.
    STRICT RULE: This function is ONLY executed when st.session_state.analysis_done is True!
    """
    profile, hist = get_customer_profile(tx["customerid"], tx["accountid"])
    feats = compute_context_features(tx, hist)
    rules = build_fraud_rules(tx, feats)
    reasons = build_explanations(tx, feats, rules)

    # 1. Fraud Dashboard (Gauge + Probability + Recommendation)
    render_fraud_dashboard_metrics(analysis_res, key_prefix=key_prefix)

    st.divider()

    # 2. Explainable AI Reasons
    st.subheader("🧩 Explainable AI — Decision Rationale")
    with st.container(border=True):
        for icon, text_msg in reasons:
            st.markdown(f"{icon}&nbsp;&nbsp;{text_msg}")

    st.divider()

    # 3 & 4. Customer Profile & Transaction Summary Cards
    col_a, col_b = st.columns(2)
    with col_a:
        render_customer_profile_card(profile)
    with col_b:
        st.subheader("🧾 Transaction Summary")
        with st.container(border=True):
            st.write(f"**Transaction ID:** TX-{int(tx['transactionid']):06d}")
            st.write(f"**Customer:** {tx['customer_name']}")
            st.write(f"**Account:** {tx['accountnumber']}")
            st.write(f"**Amount:** {tx['amount']:,.2f} EGP")
            st.write(f"**Channel:** {tx['channel']}")
            st.write(f"**ATM:** {tx['atmid'] if pd.notna(tx['atmid']) else '—'}")
            st.write(f"**Employee:** {tx['employeeid'] if pd.notna(tx['employeeid']) else '—'}")
            st.write(f"**Status:** {tx['status']}")
            tx_dt = pd.to_datetime(tx["transactiondate"])
            st.write(f"**Timestamp:** {tx_dt.strftime('%Y-%m-%d %H:%M')}")
            if pd.notna(tx.get("description")) and tx.get("description"):
                st.write(f"**Description:** {tx['description']}")

    st.divider()

    # 5. Timeline
    render_customer_timeline(hist)

    st.divider()

    # 6. Fraud Rules Panel
    st.subheader("📏 Fraud Rules Triggered")
    chips_html = ""
    for r_name, r_triggered in rules.items():
        css_cls = "rule-on" if r_triggered else "rule-off"
        icon_str = "✔" if r_triggered else "✘"
        chips_html += f"<span class='rule-chip {css_cls}'>{r_name} {icon_str}</span>"
    st.markdown(chips_html, unsafe_allow_html=True)

    st.divider()

    # 7. Similar Fraud Cases
    render_similar_cases_table(tx)

    st.divider()

    # 8. Feature Importance
    render_feature_importance_chart(analysis_res["model"], analysis_res["feature_cols"])

    st.divider()

    # 9. Recommended Actions & Save
    render_recommended_actions(int(tx["transactionid"]), analysis_res["risk_level"], key_prefix=key_prefix)


def render_fraud_detection_page():
    st.title("🚨 Enterprise Fraud Monitoring & Analysis")
    st.caption("Real-time digital banking transaction risk assessment and hybrid AI fraud detection.")

    # Initialize Session States
    if "pending_transaction" not in st.session_state:
        st.session_state.pending_transaction = None
    if "confirmed_transaction" not in st.session_state:
        st.session_state.confirmed_transaction = None
    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None

    try:
        model, encoders, feature_cols, default_threshold = load_model_bundle()
    except Exception as err:
        st.error(f"❌ Model bundle loading error: {err}")
        return

    threshold = st.sidebar.number_input(
        "🚩 Auto-Suspicion Amount Threshold (EGP)",
        min_value=0.0,
        value=float(default_threshold),
        step=1000.0,
        help="Transactions exceeding this amount trigger immediate high-value suspicion rules."
    )

    # Fetch live stats for today
    try:
        today_date = pd.Timestamp.now().date()
        today_txns = run_query(
            "SELECT * FROM transactions WHERE transactiondate::date = :d;",
            {"d": today_date}
        )
    except Exception:
        today_txns = pd.DataFrame()

    avg_score_today = 0.0
    high_risk_today = 0

    render_today_stats(today_txns, high_risk_today, avg_score_today)

    st.divider()

    tab_new, tab_existing = st.tabs(["➕ Create New Transaction", "📋 Existing Transactions"])

    # ================= TAB 1: NEW TRANSACTION WORKFLOW =================
    with tab_new:
        try:
            customers_df = run_query("SELECT customerid, (firstname || ' ' || lastname) AS full_name FROM customers ORDER BY customerid;")
            accounts_df = run_query("SELECT accountid, customerid, accountnumber, accounttype, balance FROM accounts ORDER BY accountid;")
            atms_df = run_query("SELECT atmid, location FROM atms ORDER BY atmid;")
            employees_df = run_query("SELECT employeeid, (firstname || ' ' || lastname) AS full_name FROM employees ORDER BY employeeid;")
            branches_df = run_query("SELECT branchid, branchname FROM branches ORDER BY branchid;")
        except Exception as e:
            st.error(f"Failed to fetch database lookup options: {e}")
            return

        # Stage 1: Fill Form
        if not st.session_state.pending_transaction and not st.session_state.confirmed_transaction:
            render_transaction_form(customers_df, accounts_df, atms_df, employees_df, branches_df, encoders)

        # Stage 2 & 3: Preview (Confirm Transaction clicked)
        elif st.session_state.pending_transaction and not st.session_state.confirmed_transaction:
            render_transaction_preview()

        # Stage 4 & 5: Saved & Retrieved Details
        elif st.session_state.confirmed_transaction:
            saved_id = st.session_state.confirmed_transaction
            tx = render_saved_transaction_details(saved_id)

            if tx is not None:
                st.divider()

                # Stage 6: Analyze Transaction Button
                if not st.session_state.analysis_done:
                    st.info("💡 Transaction saved in database. Click 'Analyze Transaction' below to evaluate fraud risk.")
                    if st.button("🧠 Analyze Transaction", type="primary", use_container_width=True, key="btn_analyze_new"):
                        hist = run_query("SELECT * FROM transactions WHERE accountid = :aid;", {"aid": int(tx["accountid"])})
                        analysis_res = predict_fraud(tx, hist, custom_threshold=threshold)
                        st.session_state.prediction_result = analysis_res
                        st.session_state.analysis_done = True
                        st.rerun()

                # Stage 7: Display Full Dashboard AFTER Clicking Analyze
                if st.session_state.analysis_done and st.session_state.prediction_result:
                    render_full_analysis_sections(tx, st.session_state.prediction_result, key_prefix="new_tx")

                st.divider()
                if st.button("➕ Create Another Transaction", use_container_width=True):
                    st.session_state.pending_transaction = None
                    st.session_state.confirmed_transaction = None
                    st.session_state.analysis_done = False
                    st.session_state.prediction_result = None
                    st.rerun()

    # ================= TAB 2: EXISTING TRANSACTIONS =================
    with tab_existing:
        st.subheader("🔍 Select & Analyze Existing Transaction")

        try:
            txns_df = run_query(
                """
                SELECT
                    t.transactionid, t.accountid, t.atmid, t.employeeid,
                    t.transactiondate, t.transactiontype, t.amount, t.channel,
                    t.status, t.isfraud,
                    a.accountnumber, a.customerid,
                    CONCAT(c.firstname, ' ', c.lastname) AS customer_name
                FROM transactions t
                JOIN accounts a ON t.accountid = a.accountid
                JOIN customers c ON a.customerid = c.customerid
                ORDER BY t.transactiondate DESC
                LIMIT 300;
                """
            )
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")
            txns_df = pd.DataFrame()

        if txns_df.empty:
            st.warning("No transaction records found in database.")
        else:
            def build_label(r):
                dt_str = pd.to_datetime(r['transactiondate']).strftime('%Y-%m-%d')
                return f"TX-{int(r['transactionid']):06d} | {r['customer_name']} | {r['accountnumber']} | {r['amount']:,.0f} EGP | {dt_str}"

            txns_df["label"] = txns_df.apply(build_label, axis=1)

            selected_label = st.selectbox("Choose Transaction to Inspect", txns_df["label"].tolist(), key="select_existing_tx")
            tx_row = txns_df[txns_df["label"] == selected_label].iloc[0]

            if st.button("🧠 Analyze Selected Transaction", type="primary", use_container_width=True, key="btn_analyze_existing"):
                st.session_state.selected_existing_id = int(tx_row["transactionid"])
                st.session_state.existing_analysis_done = True

            if st.session_state.get("existing_analysis_done") and st.session_state.get("selected_existing_id") == int(tx_row["transactionid"]):
                full_tx = get_transaction_by_id(int(tx_row["transactionid"]))
                if full_tx is not None:
                    hist = run_query("SELECT * FROM transactions WHERE accountid = :aid;", {"aid": int(full_tx["accountid"])})
                    res = predict_fraud(full_tx, hist, custom_threshold=threshold)
                    st.divider()
                    render_full_analysis_sections(full_tx, res, key_prefix="existing_tx")


# ============================================================================
# PAGE 3: AI BANKING ASSISTANT
# ============================================================================
def render_assistant_page():
    st.title("🤖 AI Banking Assistant")
    st.caption("Ask questions about transactions, accounts, and customer risk in natural English or Arabic.")

    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not groq_key and not gemini_key:
        st.warning("⚠️ Neither GROQ_API_KEY nor GEMINI_API_KEY is configured in your environment / .env file.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    SCHEMA_CONTEXT = """
    You are an expert Banking Data Assistant. The PostgreSQL database contains these tables:
    - branches(branchid, branchname, city, region, address, phone)
    - employees(employeeid, branchid, firstname, lastname, position, hiredate, phone, email)
    - customers(customerid, firstname, lastname, dateofbirth, gender, email, phone, address, city, joindate)
    - accounts(accountid, customerid, branchid, accountnumber, accounttype, opendate, balance, status)
    - atms(atmid, branchid, location, status)
    - transactions(transactionid, accountid, atmid, employeeid, transactiondate, transactiontype, amount, channel, status, isfraud, description)
    - loans(loanid, customerid, employeeid, loantype, amount, interestrate, termmonths, enddate, status)
    - creditcards(cardid, customerid, cardnumber, cardtype, issuedate, expirydate, creditlimit, status)

    Instructions:
    1. Respond with a concise answer explaining the insights.
    2. If relevant, include a read-only PostgreSQL query enclosed in ```sql code blocks.
    3. Match the user's language (Arabic or English).
    """

    for role, text_content in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text_content)

    user_input = st.chat_input("Ask about high-risk customers, recent fraudulent transactions, account balances...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            reply = ""
            if groq_key:
                try:
                    from groq import Groq
                    client = Groq(api_key=groq_key)
                    comp = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": SCHEMA_CONTEXT},
                            {"role": "user", "content": user_input},
                        ],
                        temperature=0.3,
                        max_tokens=1024,
                    )
                    reply = comp.choices[0].message.content
                except Exception as e:
                    reply = f"Groq API error: {e}"
            elif gemini_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"{SCHEMA_CONTEXT}\n\nUser Question: {user_input}",
                    )
                    reply = res.text
                except Exception as e:
                    reply = f"Gemini API error: {e}"
            else:
                reply = "AI Assistant key missing. Please set GROQ_API_KEY or GEMINI_API_KEY in .env."

            st.markdown(reply)

            if "```sql" in reply:
                sql_block = reply.split("```sql")[1].split("```")[0].strip()
                if st.button("▶️ Run generated SQL query on PostgreSQL", key=f"run_sql_{len(st.session_state.chat_history)}"):
                    try:
                        validate_readonly_sql(sql_block)
                        res_df = run_query(sql_block)
                        st.dataframe(res_df, use_container_width=True)
                    except Exception as sql_err:
                        st.error(f"SQL execution error: {sql_err}")

        st.session_state.chat_history.append(("assistant", reply))


# ============================================================================
# SIDEBAR NAVIGATION & MAIN ROUTER
# ============================================================================
st.sidebar.title("🏦 Smart Banking Analytics")
st.sidebar.caption("Enterprise Fraud Detection & Decision System")

page_selection = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Dashboard", "🚨 Fraud Detection & Workflow", "🤖 AI Banking Assistant"],
)

if page_selection == "📊 Executive Dashboard":
    render_dashboard_page()

elif page_selection == "🚨 Fraud Detection & Workflow":
    render_fraud_detection_page()

elif page_selection == "🤖 AI Banking Assistant":
    render_assistant_page()