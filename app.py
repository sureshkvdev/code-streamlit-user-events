import streamlit as st
from db_manager import DuckDBManager
import plotly.express as px

st.set_page_config(page_title="User Analytics Dashboard", layout="wide")
st.title("📊 User Engagement Analytics")

# Initialize DB
@st.cache_resource
def init_db():
    db = DuckDBManager(":memory:")
    db.create_tables()
    db.load_csv_data("user_events.csv")
    return db

db = init_db()

# Sidebar
st.sidebar.header("Analytics Options")
view = st.sidebar.selectbox(
    "Select Analysis",
    ["Engagement Segmentation", "User Type Breakdown", "Category Performance", "Time-Series", "Conversion Funnel"]
)

# Display analytics
if view == "Engagement Segmentation":
    st.header("Engagement Segmentation")
    df = db.get_engagement_segmentation()
    st.dataframe(df, use_container_width=True)
    
elif view == "User Type Breakdown":
    st.header("User Type Analysis")
    df = db.get_user_type_breakdown()
    st.dataframe(df, use_container_width=True)
    
elif view == "Category Performance":
    st.header("Category Performance")
    df = db.get_category_performance()
    st.dataframe(df, use_container_width=True)
    
elif view == "Time-Series":
    st.header("Time-Series Conversions")
    granularity = st.selectbox("Granularity", ["day", "week", "month"])
    df = db.get_timeseries_conversion(granularity)
    st.dataframe(df, use_container_width=True)
    
elif view == "Conversion Funnel":
    st.header("Conversion Funnel")
    df = db.get_conversion_funnel()
    st.dataframe(df, use_container_width=True)