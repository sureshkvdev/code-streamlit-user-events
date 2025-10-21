# 📊 User Engagement Analytics Dashboard

A comprehensive Streamlit dashboard for analyzing user engagement data with interactive visualizations and real-time filtering capabilities.

## 🚀 Features

### 📈 Dashboard Overview
- **Key Metrics**: Total sessions, unique users, conversion rates, revenue
- **Quick Insights**: Category performance and user type breakdown charts
- **Recent Trends**: Time-series analysis of sessions and conversion rates

### 🎯 Engagement Segmentation
- **User Segmentation**: Low, Medium, High engagement segments
- **Interactive Charts**: Bar charts showing user distribution and conversion rates
- **Revenue Analysis**: Revenue breakdown by engagement level

### 👥 User Type Breakdown
- **New vs Returning**: Comparative analysis of user types
- **Visual Comparisons**: Pie charts and bar charts for easy comparison
- **Performance Metrics**: Conversion rates and revenue by user type

### 🏷️ Category Performance
- **Product Categories**: Electronics, Clothing, Home & Garden, Sports, Books
- **Revenue Analysis**: Total revenue and average order value by category
- **Conversion Tracking**: Category-specific conversion rates

### 📅 Time-Series Analysis
- **Flexible Granularity**: Daily, weekly, or monthly views
- **Trend Analysis**: Sessions, conversion rates, and revenue over time
- **User Behavior**: New vs returning user trends

### 🔄 Conversion Funnel
- **Funnel Visualization**: Step-by-step conversion analysis
- **Stage Performance**: Conversion rates at each funnel stage
- **Revenue Tracking**: Revenue generation through the funnel

### 📋 Raw Data Explorer
- **Advanced Filtering**: Filter by category, user type, conversion status, revenue
- **Pagination**: Navigate through large datasets efficiently
- **Data Export**: Download filtered data as CSV
- **Real-time Stats**: Summary metrics for filtered data

## 🎨 UI Enhancements

- **Modern Design**: Gradient headers and rounded corners
- **Responsive Layout**: Optimized for different screen sizes
- **Interactive Elements**: Hover effects and smooth transitions
- **Color-coded Charts**: Intuitive color schemes for better readability
- **Sidebar Information**: Quick stats and feature overview

## 🛠️ Technical Stack

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **DuckDB**: High-performance analytics database
- **Pandas**: Data manipulation and analysis
- **Custom CSS**: Enhanced styling and user experience

## 📊 Data Structure

The dashboard analyzes user events data with the following fields:
- `user_id`: Unique user identifier
- `session_id`: Unique session identifier
- `page_views`: Number of pages viewed
- `time_on_page`: Time spent on site (seconds)
- `events_triggered`: Number of user interactions
- `category`: Product category
- `is_returning`: Boolean for returning users
- `converted`: Boolean for conversions
- `revenue`: Revenue generated
- `session_date`: Date of the session

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

3. **Access the Dashboard**:
   Open your browser to `http://localhost:8501`

## 📈 Key Metrics Tracked

- **Engagement Score**: Calculated as (page_views × 0.3) + (time_on_page × 0.4) + (events_triggered × 0.3)
- **Conversion Rate**: Percentage of sessions that result in conversions
- **Average Order Value**: Average revenue per conversion
- **User Retention**: Analysis of new vs returning users
- **Category Performance**: Revenue and conversion metrics by product category

## 🔧 Customization

The dashboard is highly customizable:
- **Chart Types**: Easily modify chart types and colors
- **Metrics**: Add or remove key performance indicators
- **Filters**: Extend filtering capabilities
- **Styling**: Modify CSS for brand-specific theming

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices
- Different screen resolutions

## 🎯 Use Cases

- **E-commerce Analytics**: Track user behavior and conversion funnels
- **Marketing Analysis**: Measure campaign effectiveness
- **Product Performance**: Analyze category-specific metrics
- **User Segmentation**: Identify high-value user segments
- **Business Intelligence**: Generate actionable insights from user data

---

*Built with ❤️ using Streamlit and Plotly*
