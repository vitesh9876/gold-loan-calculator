import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_total_months(start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
    if end_date.day <= 10:
        months -= 1
    return months

def get_interest_rate(amount):
    return 2 if amount >= 5000 else 3

def calculate_gold_loan(principal, start_date, end_date):
    total_months = calculate_total_months(start_date, end_date)
    total_interest = 0
    original_principal = principal
    month_counter = 0

    while month_counter < total_months:
        months_this_cycle = min(12, total_months - month_counter)
        rate = get_interest_rate(principal)
        monthly_interest = (principal / 100) * rate
        cycle_interest = monthly_interest * months_this_cycle

        total_interest += cycle_interest
        principal += cycle_interest
        month_counter += months_this_cycle

    total_payable = original_principal + total_interest
    return total_months, round(total_interest, 2), round(total_payable, 2)

# --- Streamlit UI ---

st.set_page_config(page_title="Praveen Kumar Finance Calculator", layout="centered")
st.title("🏦 Praveen Kumar Finance Calculator")

with st.form("gold_loan_form"):
    amount = st.number_input("Enter Loan Amount (₹):", min_value=100.0, step=100.0)
    start_date = st.date_input("Loan Taken Date", value=date.today())
    end_date = st.date_input("Loan Return Date", value=date.today())
    calculate = st.form_submit_button("Calculate")

if calculate:
    if end_date <= start_date:
        st.error("❌ Return date must be after the loan date.")
    else:
        months, interest, payable = calculate_gold_loan(amount, start_date, end_date)
        st.success("✅ Calculation Complete!")
        st.markdown(f"""
        ### 📊 Summary
        - 📅 **Total Months Charged:** {months}
        - 💰 **Total Interest:** ₹{interest}
        - 🧾 **Total Payable:** ₹{payable}
        """)
