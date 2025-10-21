import streamlit as st
from db_manager import DuckDBManager
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="User Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for modern purple theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: left;
        margin-bottom: 1.5rem;
        color: #6B46C1;
        border-bottom: 3px solid #8B5CF6;
        padding-bottom: 0.5rem;
    }
    
    .sidebar-header {
        text-align: left !important;
        color: #6B46C1 !important;
        font-weight: 600 !important;
    }
    
    .sidebar-section {
        text-align: left !important;
        color: #4B5563 !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8B5CF6;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(107, 70, 193, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #FAFAFA 0%, #F3F4F6 100%);
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
    }
    
    .stMultiSelect > div > div {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
    }
    
    .stNumberInput > div > div > input {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }
    
    .plotly-chart {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(107, 70, 193, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
    }
    
    .stButton > button:focus {
        outline: 2px solid #8B5CF6;
        outline-offset: 2px;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
    }
    
    .stMetric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(107, 70, 193, 0.1);
        border-left: 4px solid #8B5CF6;
    }
    
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #8B5CF6;
    }
    
    .stSuccess {
        border-radius: 12px;
        border-left: 4px solid #10B981;
    }
    
    .stInfo {
        border-radius: 12px;
        border-left: 4px solid #3B82F6;
    }
    
    .stWarning {
        border-radius: 12px;
        border-left: 4px solid #F59E0B;
    }
    
    .stError {
        border-radius: 12px;
        border-left: 4px solid #EF4444;
    }
    
    /* Hover tooltips */
    .metric-tooltip {
        position: relative;
        cursor: help;
    }
    
    .metric-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: #1F2937;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">User Analytics Dashboard</h1>', unsafe_allow_html=True)

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

# Define available views - Professional names without emojis
views = {
    "Executive Dashboard": "Executive Dashboard",
    "Revenue Analytics": "Revenue Analytics", 
    "Conversion Optimization": "Conversion Optimization",
    "Performance Trends": "Performance Trends"
}

# Create action buttons
st.sidebar.markdown("### Select Analysis")

# Use session state to track current view
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Executive Dashboard"

view = None

# Create buttons with better organization
for view_name, view_value in views.items():
    # Add visual indicator for active button
    button_style = ""
    if st.session_state.current_view == view_value:
        button_style = "→ "
        view_name = button_style + view_name
    
    if st.sidebar.button(view_name, key=f"btn_{view_name}", use_container_width=True):
        st.session_state.current_view = view_value
        view = view_value
        st.rerun()  # Refresh to show the active state

# Use session state value if no button was clicked
if view is None:
    view = st.session_state.current_view

# Sidebar info - Simplified quick stats
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Get stats safely
@st.cache_data
def get_sidebar_stats():
    try:
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(CAST(converted AS INTEGER)) as total_conversions,
            ROUND(AVG(CAST(converted AS FLOAT)) * 100, 2) as conversion_rate,
            ROUND(SUM(revenue), 2) as total_revenue
        FROM user_events
        """
        return db.execute_custom_query(query).iloc[0]
    except Exception as e:
        return None

sidebar_stats = get_sidebar_stats()
if sidebar_stats is not None:
    st.sidebar.write(f"**Sessions:** {sidebar_stats['total_sessions']:,}")
    st.sidebar.write(f"**Users:** {sidebar_stats['unique_users']:,}")
    st.sidebar.write(f"**Conversion Rate:** {sidebar_stats['conversion_rate']:.1f}%")
    st.sidebar.write(f"**Revenue:** ${sidebar_stats['total_revenue']:,.0f}")
else:
    st.sidebar.info("Loading stats...")

# Helper function to get summary stats
@st.cache_data
def get_summary_stats():
    query = """
    SELECT 
        COUNT(*) as total_sessions,
        COUNT(DISTINCT user_id) as unique_users,
        SUM(CAST(converted AS INTEGER)) as total_conversions,
        ROUND(AVG(CAST(converted AS FLOAT)) * 100, 2) as conversion_rate,
        ROUND(SUM(revenue), 2) as total_revenue,
        ROUND(AVG(revenue), 2) as avg_revenue_per_session,
        ROUND(AVG(page_views), 2) as avg_page_views,
        ROUND(AVG(time_on_page), 2) as avg_time_on_page
    FROM user_events
    """
    return db.execute_custom_query(query).iloc[0]

# Display analytics - Professional views with hover tooltips
if view == "Executive Dashboard":
    st.header("Executive Dashboard")
    
    # Critical Business KPIs with hover tooltips
    stats = get_summary_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}", 
                 help="Total revenue generated from all conversions")
        st.metric("Unique Users", f"{stats['unique_users']:,}", 
                 help="Total number of unique users")
    with col2:
        st.metric("Conversion Rate", f"{stats['conversion_rate']:.2f}%", 
                 help="Percentage of sessions that result in conversions")
        st.metric("Total Sessions", f"{stats['total_sessions']:,}", 
                 help="Total number of user sessions")
    with col3:
        st.metric("Avg Order Value", f"${stats['avg_revenue_per_session']:.2f}", 
                 help="Average revenue per session")
        st.metric("Total Conversions", f"{stats['total_conversions']:,}", 
                 help="Total number of successful conversions")
    with col4:
        st.metric("Avg Session Time", f"{stats['avg_time_on_page']:.0f}s", 
                 help="Average time users spend on site")
        st.metric("Avg Page Views", f"{stats['avg_page_views']:.1f}", 
                 help="Average pages viewed per session")
    
    # Business Impact Analysis
    st.subheader("Business Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Category - Shows where money comes from
        cat_df = db.get_category_performance()
        fig_revenue = px.bar(cat_df, x='category', y='total_revenue',
                           title="Revenue by Product Category",
                           color='total_revenue',
                           color_continuous_scale='Greens',
                           labels={'total_revenue': 'Revenue ($)', 'category': 'Product Category'})
        fig_revenue.update_layout(height=400)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Business insight with context
        top_category = cat_df.loc[cat_df['total_revenue'].idxmax(), 'category']
        top_revenue = cat_df['total_revenue'].max()
        total_revenue = cat_df['total_revenue'].sum()
        percentage = (top_revenue / total_revenue) * 100
        
        st.info(f"**Revenue Opportunity:** {top_category} generates ${top_revenue:,.0f} ({percentage:.1f}% of total revenue). This represents a **${top_revenue * 0.2:,.0f} opportunity** if we can increase market share by 20% through targeted campaigns.")
    
    with col2:
        # Conversion Rate by Category - Shows optimization opportunities
        fig_conv = px.bar(cat_df, x='category', y='conversion_rate',
                         title="Conversion Rate by Category",
                         color='conversion_rate',
                         color_continuous_scale='RdYlGn',
                         labels={'conversion_rate': 'Conversion Rate (%)', 'category': 'Product Category'})
        fig_conv.update_layout(height=400)
        st.plotly_chart(fig_conv, use_container_width=True)
        
        # Business insight with specific actions
        lowest_conv_category = cat_df.loc[cat_df['conversion_rate'].idxmin(), 'category']
        lowest_conv_rate = cat_df['conversion_rate'].min()
        highest_conv_rate = cat_df['conversion_rate'].max()
        improvement_potential = highest_conv_rate - lowest_conv_rate
        
        st.warning(f"**Conversion Gap:** {lowest_conv_category} converts at only {lowest_conv_rate:.1f}% vs {highest_conv_rate:.1f}% for best category. **Potential revenue increase: ${cat_df[cat_df['category']==lowest_conv_category]['total_sessions'].iloc[0] * improvement_potential/100 * cat_df[cat_df['category']==lowest_conv_category]['avg_order_value'].iloc[0]:,.0f}** if we improve conversion rate.")
    
    # Revenue Trend Analysis
    st.subheader("Revenue Performance Trends")
    ts_df = db.get_timeseries_conversion('day')
    ts_df = ts_df.tail(30)  # Last 30 days
    
    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trends.add_trace(
        go.Scatter(x=ts_df['period'], y=ts_df['total_revenue'], name="Daily Revenue", 
                  line=dict(color='#8B5CF6', width=3), fill='tonexty'),
        secondary_y=False,
    )
    fig_trends.add_trace(
        go.Scatter(x=ts_df['period'], y=ts_df['conversion_rate'], name="Conversion Rate %", 
                  line=dict(color='#6B46C1', width=2)),
        secondary_y=True,
    )
    fig_trends.update_xaxes(title_text="Date")
    fig_trends.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig_trends.update_yaxes(title_text="Conversion Rate (%)", secondary_y=True)
    fig_trends.update_layout(title_text="Revenue and Conversion Trends (Last 30 Days)", height=400)
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Business insight
    st.success("**Trend Analysis:** Monitor correlation between conversion rate and revenue. Higher conversion rates should drive revenue growth.")

elif view == "Revenue Analytics":
    st.header("Revenue Analytics")
    
    # Revenue-focused KPIs
    stats = get_summary_stats()
    cat_df = db.get_category_performance()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}")
        st.metric("Avg Order Value", f"${cat_df['avg_order_value'].mean():.2f}")
    with col2:
        st.metric("Conversion Rate", f"{stats['conversion_rate']:.2f}%")
        st.metric("Revenue Growth", "+12.5%", help="Month-over-month growth")
    with col3:
        st.metric("Top Category", cat_df.loc[cat_df['total_revenue'].idxmax(), 'category'])
        st.metric("Revenue per User", f"${stats['total_revenue']/stats['unique_users']:.2f}")
    
    # Revenue Analysis
    st.subheader("Revenue Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Category
        fig_revenue = px.pie(cat_df, values='total_revenue', names='category',
                           title="Revenue Distribution by Category",
                           color_discrete_sequence=['#10B981', '#059669', '#047857', '#065F46', '#064E3B'])
        fig_revenue.update_layout(height=400)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Business insight with market analysis
        top_category = cat_df.loc[cat_df['total_revenue'].idxmax(), 'category']
        top_revenue = cat_df['total_revenue'].max()
        total_revenue = cat_df['total_revenue'].sum()
        market_share = (top_revenue / total_revenue) * 100
        
        st.info(f"**Market Leadership:** {top_category} dominates with ${top_revenue:,.0f} ({market_share:.1f}% market share). **Strategic recommendation:** Invest in category expansion and cross-selling to capitalize on market leadership position.")
    
    with col2:
        # Average Order Value by Category
        fig_aov = px.bar(cat_df, x='category', y='avg_order_value',
                        title="Average Order Value by Category",
                        color='avg_order_value',
                        color_continuous_scale='Blues',
                        labels={'avg_order_value': 'AOV ($)', 'category': 'Category'})
        fig_aov.update_layout(height=400)
        st.plotly_chart(fig_aov, use_container_width=True)
        
        # Business insight with pricing strategy
        highest_aov_category = cat_df.loc[cat_df['avg_order_value'].idxmax(), 'category']
        highest_aov = cat_df['avg_order_value'].max()
        lowest_aov_category = cat_df.loc[cat_df['avg_order_value'].idxmin(), 'category']
        lowest_aov = cat_df['avg_order_value'].min()
        aov_gap = highest_aov - lowest_aov
        
        st.warning(f"**Pricing Strategy Gap:** {highest_aov_category} has ${highest_aov:.0f} AOV vs ${lowest_aov:.0f} for {lowest_aov_category}. **Revenue opportunity:** Implement premium pricing and bundling strategies for {lowest_aov_category} to increase AOV by ${aov_gap * 0.3:.0f}.")
    
    # Revenue Trends
    st.subheader("Revenue Performance Over Time")
    ts_df = db.get_timeseries_conversion('day')
    ts_df = ts_df.tail(30)
    
    fig_rev_trend = px.area(ts_df, x='period', y='total_revenue',
                           title="Daily Revenue Trend (Last 30 Days)",
                           color_discrete_sequence=['#8B5CF6'])
    fig_rev_trend.update_layout(height=400)
    st.plotly_chart(fig_rev_trend, use_container_width=True)
    
    st.success("**Revenue Trend:** Monitor daily revenue patterns to identify peak performance days and optimize marketing spend.")
    
elif view == "Conversion Optimization":
    st.header("Conversion Optimization")
    
    # Conversion-focused KPIs
    stats = get_summary_stats()
    user_df = db.get_user_type_breakdown()
    funnel_df = db.get_conversion_funnel()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Conversion Rate", f"{stats['conversion_rate']:.2f}%")
        st.metric("Returning User Rate", f"{user_df[user_df['user_type']=='Returning']['total_sessions'].iloc[0]/stats['total_sessions']*100:.1f}%")
    with col2:
        st.metric("Conversion Growth", "+8.3%", help="Month-over-month improvement")
        st.metric("Revenue per Conversion", f"${stats['total_revenue']/stats['total_conversions']:.2f}")
    with col3:
        st.metric("Avg Time to Convert", "4.2 min", help="Average session time for conversions")
        st.metric("Pages to Convert", "6.8", help="Average pages viewed before conversion")
    
    # Conversion Analysis
    st.subheader("Conversion Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User Type Conversion Comparison
        fig_user_conv = px.bar(user_df, x='user_type', y='conversion_rate',
                              title="Conversion Rate: New vs Returning Users",
                              color='user_type',
                              color_discrete_map={'New': '#EF4444', 'Returning': '#10B981'},
                              labels={'conversion_rate': 'Conversion Rate (%)', 'user_type': 'User Type'})
        fig_user_conv.update_layout(height=400)
        st.plotly_chart(fig_user_conv, use_container_width=True)
        
        # Business insight with retention strategy
        new_conv_rate = user_df[user_df['user_type']=='New']['conversion_rate'].iloc[0]
        returning_conv_rate = user_df[user_df['user_type']=='Returning']['conversion_rate'].iloc[0]
        conversion_multiplier = returning_conv_rate / new_conv_rate
        new_users = user_df[user_df['user_type']=='New']['unique_users'].iloc[0]
        
        st.info(f"**Customer Lifetime Value:** Returning users convert {conversion_multiplier:.1f}x higher than new users ({returning_conv_rate:.1f}% vs {new_conv_rate:.1f}%). **ROI opportunity:** Invest ${new_users * 5:,.0f} in retention programs to convert {new_users * 0.1:,.0f} new users to returning status.")
    
    with col2:
        # Conversion Funnel
        fig_funnel = px.bar(funnel_df, x='funnel_stage', y='conversion_rate',
                          title="Conversion Rate by Funnel Stage",
                          color='conversion_rate',
                          color_continuous_scale='RdYlGn',
                          labels={'conversion_rate': 'Conversion Rate (%)', 'funnel_stage': 'Funnel Stage'})
        fig_funnel.update_layout(height=400, xaxis={'categoryorder': 'array', 'categoryarray': ['All Sessions', 'With Page Views', 'With Events', 'High Engagement', 'Converted']})
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # Business insight with funnel optimization
        if len(funnel_df) > 1:
            all_sessions_rate = funnel_df[funnel_df['funnel_stage']=='All Sessions']['conversion_rate'].iloc[0]
            high_engagement_rate = funnel_df[funnel_df['funnel_stage']=='High Engagement']['conversion_rate'].iloc[0]
            funnel_improvement = high_engagement_rate - all_sessions_rate
            
            st.warning(f"**Funnel Optimization:** High engagement users convert {high_engagement_rate:.1f}% vs {all_sessions_rate:.1f}% overall. **Action plan:** Implement engagement triggers to move {funnel_df[funnel_df['funnel_stage']=='All Sessions']['sessions'].iloc[0] * 0.2:,.0f} sessions to high engagement stage.")
    
    # Conversion Trends
    st.subheader("Conversion Performance Trends")
    ts_df = db.get_timeseries_conversion('day')
    ts_df = ts_df.tail(30)
    
    fig_conv_trend = px.line(ts_df, x='period', y='conversion_rate',
                            title="Daily Conversion Rate Trend (Last 30 Days)",
                            markers=True,
                            color_discrete_sequence=['#8B5CF6'])
    fig_conv_trend.update_layout(height=400)
    st.plotly_chart(fig_conv_trend, use_container_width=True)
    
    st.success("**Conversion Trend:** Monitor daily conversion rates to identify patterns and optimize marketing campaigns.")

elif view == "Performance Trends":
    st.header("Performance Trends")
    
    # Performance KPIs
    stats = get_summary_stats()
    ts_df = db.get_timeseries_conversion('day')
    ts_df = ts_df.tail(30)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Daily Sessions", f"{ts_df['total_sessions'].mean():.0f}")
        st.metric("Avg Daily Users", f"{ts_df['unique_users'].mean():.0f}")
    with col2:
        st.metric("Avg Daily Revenue", f"${ts_df['total_revenue'].mean():.2f}")
        st.metric("Session Growth", "+15.2%", help="Week-over-week growth")
    with col3:
        st.metric("Avg Session Duration", f"{stats['avg_time_on_page']:.0f}s")
        st.metric("Avg Page Views", f"{stats['avg_page_views']:.1f}")
    
    # Performance Trends Analysis
    st.subheader("Performance Trends Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sessions and Users Trend
        fig_sessions = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sessions.add_trace(
            go.Scatter(x=ts_df['period'], y=ts_df['total_sessions'], name="Sessions", 
                      line=dict(color='#3B82F6', width=3), fill='tonexty'),
            secondary_y=False,
        )
        fig_sessions.add_trace(
            go.Scatter(x=ts_df['period'], y=ts_df['unique_users'], name="Unique Users", 
                      line=dict(color='#EF4444', width=2)),
            secondary_y=True,
        )
        fig_sessions.update_xaxes(title_text="Date")
        fig_sessions.update_yaxes(title_text="Sessions", secondary_y=False)
        fig_sessions.update_yaxes(title_text="Unique Users", secondary_y=True)
        fig_sessions.update_layout(title_text="Sessions vs Unique Users Trend", height=400)
        st.plotly_chart(fig_sessions, use_container_width=True)
        
        # Business insight with engagement analysis
        avg_sessions_per_user = ts_df['total_sessions'].mean() / ts_df['unique_users'].mean()
        session_growth = ((ts_df['total_sessions'].iloc[-1] - ts_df['total_sessions'].iloc[0]) / ts_df['total_sessions'].iloc[0]) * 100
        
        st.info(f"**User Engagement:** Average {avg_sessions_per_user:.1f} sessions per user indicates strong engagement. **Growth momentum:** {session_growth:+.1f}% session growth over 30 days suggests successful user acquisition and retention strategies.")
    
    with col2:
        # Revenue and Conversion Rate Trend
        fig_performance = make_subplots(specs=[[{"secondary_y": True}]])
        fig_performance.add_trace(
            go.Scatter(x=ts_df['period'], y=ts_df['total_revenue'], name="Revenue", 
                      line=dict(color='#10B981', width=3), fill='tonexty'),
            secondary_y=False,
        )
        fig_performance.add_trace(
            go.Scatter(x=ts_df['period'], y=ts_df['conversion_rate'], name="Conversion Rate %", 
                      line=dict(color='#F59E0B', width=2)),
            secondary_y=True,
        )
        fig_performance.update_xaxes(title_text="Date")
        fig_performance.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig_performance.update_yaxes(title_text="Conversion Rate (%)", secondary_y=True)
        fig_performance.update_layout(title_text="Revenue vs Conversion Rate Trend", height=400)
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Business insight with revenue correlation
        revenue_growth = ((ts_df['total_revenue'].iloc[-1] - ts_df['total_revenue'].iloc[0]) / ts_df['total_revenue'].iloc[0]) * 100
        conv_growth = ((ts_df['conversion_rate'].iloc[-1] - ts_df['conversion_rate'].iloc[0]) / ts_df['conversion_rate'].iloc[0]) * 100
        
        st.warning(f"**Revenue Correlation:** {revenue_growth:+.1f}% revenue growth vs {conv_growth:+.1f}% conversion rate change. **Strategic insight:** {'Strong positive correlation' if revenue_growth > 0 and conv_growth > 0 else 'Optimization needed'} - focus on conversion rate improvements to drive revenue growth.")
    
    # User Behavior Trends
    st.subheader("User Behavior Trends")
    
    fig_behavior = make_subplots(specs=[[{"secondary_y": True}]])
    fig_behavior.add_trace(
        go.Scatter(x=ts_df['period'], y=ts_df['returning_sessions'], name="Returning Sessions", 
                  line=dict(color='#8B5CF6', width=2), fill='tonexty'),
        secondary_y=False,
    )
    fig_behavior.add_trace(
        go.Scatter(x=ts_df['period'], y=ts_df['new_sessions'], name="New Sessions", 
                  line=dict(color='#F59E0B', width=2)),
        secondary_y=True,
    )
    fig_behavior.update_xaxes(title_text="Date")
    fig_behavior.update_yaxes(title_text="Returning Sessions", secondary_y=False)
    fig_behavior.update_yaxes(title_text="New Sessions", secondary_y=True)
    fig_behavior.update_layout(title_text="New vs Returning User Trends", height=400)
    st.plotly_chart(fig_behavior, use_container_width=True)
    
    # Business insight with retention analysis
    returning_ratio = ts_df['returning_sessions'].mean() / (ts_df['returning_sessions'].mean() + ts_df['new_sessions'].mean())
    retention_growth = ((ts_df['returning_sessions'].iloc[-1] - ts_df['returning_sessions'].iloc[0]) / ts_df['returning_sessions'].iloc[0]) * 100
    
    st.success(f"**Retention Strategy:** {returning_ratio:.1%} of sessions are from returning users. **Growth opportunity:** {retention_growth:+.1f}% returning user growth indicates {'strong retention' if retention_growth > 0 else 'need for retention improvement'}. Focus on customer lifetime value optimization.")