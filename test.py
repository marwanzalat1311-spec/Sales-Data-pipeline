import pandas as pd
from pymongo import MongoClient
import streamlit as st
import plotly.express as px

# ============================
# 1) Connect to MongoDB
# ============================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "MyDatabase"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ============================
# 2) Streamlit page config
# ============================
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

# ============================
# 3) Custom Dark CSS
# ============================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(120deg, #1e1e2f 0%, #121212 100%);
        color: #f5f5f5;
    }
    .stTitle, h1, h2, h3 {
        color: #f1c40f;
        font-weight: bold;
    }
    .stDataFrame th {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    .css-18e3th9, .css-1d391kg {
        background-color: #2c2c34;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.6);
        color: #f5f5f5;
    }
    .stMarkdown, .stText, .stSubheader {
        color: #ecf0f1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌙 Retail Sales Dashboard (Dark Mode)")

# ============================
# Helper: Convert numeric columns
# ============================
def convert_numeric(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

numeric_cols = ["totalspent", "totalquantity", "totalrevenue"]

# ============================
# Load all dataframes
# ============================
dfs = {}
collections = ["TopCustomers", "BestSellingProductsByBranch", "BranchRevenueComparison",
               "MonthlySalesTrends", "SeasonalProductDemand", "StockPlanning"]

for coll in collections:
    df = pd.DataFrame(list(db[coll].find({}, {"_id":0})))
    
    # Clean column names
    df.columns = (
        df.columns.astype(str)
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
    )
    
    # Convert numeric
    df = convert_numeric(df, numeric_cols)
    
    # Parse Month if exists
    if "month" in df.columns:
        df["month"] = pd.to_datetime(df["month"], errors="coerce")

    dfs[coll] = df

# ============================
# Charts (colors stay vivid)
# ============================

# -------- Row 1 --------
col1, col2 = st.columns(2)

with col1:
    st.subheader("👑 Top Customers")
    df = dfs["TopCustomers"]
    if df.shape[0] > 0 and {"customername","totalspent"} <= set(df.columns):
        fig = px.bar(df, x="totalspent", y="customername",
                     orientation="h", text="totalspent",
                     color="totalspent", color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in TopCustomers")

with col2:
    st.subheader("🔥 Best-Selling Products")
    df = dfs["BestSellingProductsByBranch"]
    if df.shape[0] > 0 and {"productname","totalquantity"} <= set(df.columns):
        fig = px.bar(df, x="productname", y="totalquantity",
                     text="totalquantity", color="productname",
                     color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in BestSellingProducts")

# -------- Row 2 --------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏬 Branch Revenue Comparison")
    df = dfs["BranchRevenueComparison"]
    if df.shape[0] > 0 and {"branchname","totalrevenue"} <= set(df.columns):
        fig = px.bar(df, x="branchname", y="totalrevenue",
                     text="totalrevenue", color="branchname",
                     color_discrete_sequence=px.colors.qualitative.Pastel2)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in BranchRevenueComparison")

with col4:
    st.subheader("📈 Monthly Sales Trends")
    df = dfs["MonthlySalesTrends"]
    if df.shape[0] > 0 and {"month","totalrevenue"} <= set(df.columns):
        fig = px.line(df, x="month", y="totalrevenue",
                      markers=True, line_shape="linear",
                      color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in MonthlySalesTrends")

# -------- Row 3 --------
col5, col6 = st.columns(2)

with col5:
    st.subheader("🌸 Seasonal Product Demand")
    df = dfs["SeasonalProductDemand"]
    if df.shape[0] > 0 and {"month","totalquantity","productname"} <= set(df.columns):
        fig = px.line(df, x="month", y="totalquantity",
                      color="productname", markers=True,
                      color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in SeasonalProductDemand")

with col6:
    st.subheader("📦 Stock Planning by Branch")
    df = dfs["StockPlanning"]
    if df.shape[0] > 0 and {"branchname","totalquantity","productname"} <= set(df.columns):
        fig = px.scatter(df, x="branchname", y="totalquantity",
                         color="productname", size="totalquantity",
                         hover_name="productname",
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, height=300)
    else:
        st.warning("⚠️ No valid data in StockPlanning")

st.success("✅ Dashboard loaded successfully in Dark Mode!")
