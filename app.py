import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import matplotlib as plt
from dotenv import load_dotenv

# Sample data for demonstration

def load_data():

    # 12 months data

    data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Sales': [4500, 5200, 4800, 6100, 5900, 6500, 7200, 6800, 7500, 8200, 9100, 10500],
        'Expenses': [3000, 3200, 3100, 3800, 3500, 4000, 4200, 4100, 4500, 5000, 5500, 6000],
        'Category': ['Electronics', 'Fashion', 'Home', 'Electronics', 'Fashion', 'Home', 'Electronics', 'Fashion', 'Home', 'Electronics', 'Fashion', 'Home'],
        'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South', 'East', 'West']
    })
    #Add Profit Column
    data['Profit'] = data['Sales'] - data['Expenses']
    return data

#define df
df = load_data()

# KPIs
total_sales = df['Sales'].sum()
avg_expenses = df['Expenses'].mean()

m1, m2, m3 = st.columns(3)
m1.metric("Total Sales", f"${total_sales:,}")
m2.metric("Avg Expenses", f"${avg_expenses:,.0f}")
m3.metric("Status", "Active", delta="Growing")

st.markdown("---")

# --- AI Setup ---
API_KEY = "AIzaSyAQ4FzNyjcdUXjL20z15pT30yRez9CYJzo"

if API_KEY:
    genai.configure(api_key=API_KEY)
    
    # check which model are avilable
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if available_models:

        # first working model select( gemini-pro and gemini-1.5-flash)
        model_name = available_models[0]
        model = genai.GenerativeModel(model_name)
        
        # for testing
        print(f"Using model: {model_name}")
    else:
        st.error("No AI model found. Please check your API Key.")
else:
    st.error("API Key not found! Please check .env file.")


st.set_page_config(page_title = "Smart AI Sales Dashboard", layout="wide")

# CSS design

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 25px;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Smart AI Sales Dashboard")

# --- SIDEBAR ENHANCEMENT ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    # 1. Project Info
    st.info("**Smart AI Sales Dashboard**  \n*Powered by Gemini 1.5 Flash*")
    
    st.markdown("### 📊 Data Filters")
    
    # 2. Region Filter
    selected_region = st.multiselect(
        "Select Region(s):", 
        options=df['Region'].unique(), 
        default=df['Region'].unique()
    )
    
    # 3. Category Filter (Adding more depth)
    selected_category = st.multiselect(
        "Select Category:", 
        options=df['Category'].unique(), 
        default=df['Category'].unique()
    )
    
    st.markdown("---")
    st.markdown("### 🛠️ Quick Actions")
    
    # 4. Data Download Button (Great for 'Real-world' feel)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name='sales_data_report.csv',
        mime='text/csv',
    )
    
    # 5. Reset Button (Visual only, to keep UI clean)
    if st.button("🔄 Clear Cache & Refresh"):
        st.rerun()

    st.markdown("---")
    st.caption("Developed with ❤️ for Code With Gemini")

# Dono filters ko apply karna
filtered_df = df[
    (df['Region'].isin(selected_region)) & 
    (df['Category'].isin(selected_category))
]

# Layout divided 3 columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Monthly Sales Trend")
    st.line_chart(filtered_df.set_index('Month')[['Sales', 'Expenses']])

with col2:
    st.subheader("Category-wise Profit")
    #ADD Bar Chart
    st.bar_chart(filtered_df.set_index('Month')['Profit'])

# Table Analysis
# Highlight max profit in Green and min expenses in Red
st.subheader("📊 Detailed Transaction Log")
st.dataframe(filtered_df.style.background_gradient(cmap='Greens', subset=['Profit']), use_container_width=True)

# ai insights section
st.markdown("---")
st.header('AI Business Insights')
if st.button("Generate Advanced AI Insights"):
    with st.spinner("Gemini is diving deep into your regional data..."):
        # Filtered data ko string mein badalna
        data_summary = filtered_df.to_string(index=False)
        
        # Naya smart prompt
        prompt = f"""
        You are a Senior Business Strategist. Analyze this detailed sales dataset:
        {data_summary}
        
        Please provide a deep-dive analysis including:
        1. **Regional Performance**: Which region is leading and which one needs attention?
        2. **Product Strategy**: Analysis of 'Category' performance (Electronics vs Fashion vs Home).
        3. **Profitability**: Mention the month with the highest profit margin.
        4. **Action Plan**: One specific strategy to reduce 'Expenses' without hitting 'Sales'.
        
        Format the output with professional headings and use bullet points.
        """
        try:
            response = model.generate_content(prompt)
            st.success("Strategic Analysis Complete!")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- DYNAMIC FUTURE PROJECTIONS ---
st.markdown("---")
st.subheader("🔮 Smart Business Forecasting")

# last 3 months data 
last_month = df['Sales'].iloc[-1]
three_months_ago = df['Sales'].iloc[-3]

# growth rate
growth_rate = (last_month - three_months_ago) / three_months_ago

# Pridiction logic: if growth rate is positive then sales-10% grow else sales-less 10%
if growth_rate > 0:
    predicted_sales = last_month * 1.10
    msg = "Growth Trend Detected"
    color = "normal" # Green arrow
else:
    predicted_sales = last_month * 0.90
    msg = "Downshift Warning"
    color = "inverse" # Red arrow

# visual display
p1, p2, p3 = st.columns(3)

with p1:
    st.metric(label="Next Month Prediction", 
              value=f"${predicted_sales:,.0f}", 
              delta=f"{'10% Rise' if growth_rate > 0 else '-10% Drop'}",
              delta_color=color)

with p2:
    st.write(f"**Trend Analysis:** {msg}")
    st.progress(max(0.1, min(1.0, abs(growth_rate)))) # show progress rate

with p3:
    st.write("**AI Confidence:** Medium ⚠️")
    st.caption("Based on real-time historical variance.")