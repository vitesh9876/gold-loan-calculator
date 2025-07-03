import streamlit as st
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import streamlit.components.v1 as components

# ------------------ Loan Logic ------------------
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

# ------------------ PDF Generator ------------------
def generate_pdf(customer_data, loan_summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    pdf.cell(200, 10, "PRAVEEN KUMAR FINANCE", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, "Date: " + datetime.today().strftime("%d-%m-%Y"), ln=True, align='C')
    pdf.cell(200, 10, "Address: Gandhi Road, Vijayawada, Andhra Pradesh", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Customer Details", ln=True)
    pdf.set_font("Arial", '', 12)
    for label, value in customer_data.items():
        pdf.cell(200, 8, f"{label}: {value}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Loan Summary", ln=True)
    pdf.set_font("Arial", '', 12)
    for label, value in loan_summary.items():
        pdf.cell(200, 8, f"{label}: {value}", ln=True)

    filename = f"Loan_Receipt_{customer_data['Name'].replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Gold Loan Calculator", layout="centered")
st.title("\U0001F3E6 Gold Loan Finance Calculator")

# --- Loan Calculation Form ---
if "loan_done" not in st.session_state:
    st.session_state.loan_done = False

if not st.session_state.loan_done:
    with st.form("loan_form"):
        st.subheader("\U0001F4B0 Loan Details")
        amount = st.number_input("Loan Amount (₹)", min_value=100.0, step=100.0)
        start_date = st.date_input("Loan Taken Date", value=date.today())
        end_date = st.date_input("Loan Release Date", value=date.today())
        calculate = st.form_submit_button("Calculate")

    if calculate:
        if end_date <= start_date:
            st.error("❌ Return date must be after the loan date.")
        else:
            months, interest, payable = calculate_gold_loan(amount, start_date, end_date)
            st.session_state.loan_done = True
            st.session_state.amount = amount
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            st.session_state.months = months
            st.session_state.interest = interest
            st.session_state.payable = payable
            st.rerun()

# --- After Calculation ---
if st.session_state.loan_done:
    st.success("✅ Calculation Complete!")
    st.markdown(f"""
    ### \U0001F4CA Loan Summary
    - 📅 **Months Charged:** {st.session_state.months}
    - 💰 **Interest:** ₹{st.session_state.interest}
    - 🧾 **Total Payable:** ₹{st.session_state.payable}
    """)

    st.subheader("\U0001F9FE Customer Details for Receipt")
    name = st.text_input("Customer Name")
    item = st.text_input("Item Name (e.g. Gold Ring, Chain)")
    weight = st.text_input("Item Weight (e.g. 10g)")
    address = st.text_area("Customer Address")

    if name and item and weight and address:
        customer_data = {
            "Name": name,
            "Item": item,
            "Weight": weight,
            "Address": address
        }

        loan_summary = {
            "Loan Amount": f"₹{st.session_state.amount}",
            "Start Date": st.session_state.start_date.strftime("%d-%m-%Y"),
            "End Date": st.session_state.end_date.strftime("%d-%m-%Y"),
            "Months Charged": st.session_state.months,
            "Interest": f"₹{st.session_state.interest}",
            "Total Payable": f"₹{st.session_state.payable}"
        }

        st.markdown("---")
        st.markdown("### 🖨️ Print Preview")
        html_content = f'''
            <div style="font-family: Arial;">
                <h2 style="text-align:center;">PRAVEEN KUMAR FINANCE</h2>
                <p style="text-align:center;">Gandhi Road, Vijayawada, Andhra Pradesh</p>
                <p style="text-align:center;">Date: {datetime.today().strftime("%d-%m-%Y")}</p>
                <hr>
                <h4>Customer Details</h4>
                <p><b>Name:</b> {name}<br>
                <b>Item:</b> {item}<br>
                <b>Weight:</b> {weight}<br>
                <b>Address:</b> {address}</p>
                <h4>Loan Summary</h4>
                <p><b>Loan Amount:</b> ₹{st.session_state.amount}<br>
                <b>Start Date:</b> {st.session_state.start_date.strftime("%d-%m-%Y")}<br>
                <b>End Date:</b> {st.session_state.end_date.strftime("%d-%m-%Y")}<br>
                <b>Months Charged:</b> {st.session_state.months}<br>
                <b>Interest:</b> ₹{st.session_state.interest}<br>
                <b>Total Payable:</b> ₹{st.session_state.payable}</p>
            </div>
            <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px;">🖨️ Print Receipt</button>
        '''
        components.html(html_content, height=700)

        filename = generate_pdf(customer_data, loan_summary)
        with open(filename, "rb") as f:
            st.download_button("💾 Download Receipt as PDF", f, file_name=filename)
    else:
        st.warning("Please enter all customer details to enable Print and Save options.")
