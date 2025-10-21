import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class DuckDBManager:
    """
    Manages DuckDB connection and analytics queries for user engagement data.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize DuckDB connection.
        
        Args:
            db_path: Path to database file or ":memory:" for in-memory DB
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        print(f"✓ DuckDB connection established: {db_path}")
    
    def create_tables(self):
        """Create required tables for user events analytics."""
        
        # Drop table if exists to avoid conflicts
        self.conn.execute("DROP TABLE IF EXISTS user_events")
        
        # Main user events table
        create_table_sql = """
        CREATE TABLE user_events (
            user_id VARCHAR,
            session_id VARCHAR,
            page_views INTEGER,
            time_on_page INTEGER,
            events_triggered INTEGER,
            category VARCHAR,
            is_returning BOOLEAN,
            converted BOOLEAN,
            revenue DECIMAL(10, 2),
            session_date DATE,
            PRIMARY KEY (session_id)
        );
        """
        
        self.conn.execute(create_table_sql)
        print("✓ Table 'user_events' created/verified")
    
    def load_csv_data(self, csv_path: str):
        """
        Load CSV data into the user_events table.
        
        Args:
            csv_path: Path to CSV file
        """
        # Use parameterized query to avoid path issues
        csv_path = csv_path.replace('\\', '/')
        
        load_sql = f"""
        INSERT INTO user_events
        SELECT 
            user_id,
            session_id,
            page_views,
            time_on_page,
            events_triggered,
            category,
            CAST(is_returning AS BOOLEAN),
            CAST(converted AS BOOLEAN),
            revenue,
            TRY_CAST(session_date AS DATE) as session_date
        FROM read_csv_auto('{csv_path}', 
            header=true,
            dateformat='%m/%d/%Y'
        );
        """
        
        self.conn.execute(load_sql)
        count = self.conn.execute("SELECT COUNT(*) FROM user_events").fetchone()[0]
        print(f"✓ Loaded {count} records from CSV")
    
    def get_engagement_segmentation(self) -> pd.DataFrame:
        """
        Segment users by engagement level (low/medium/high).
        
        Engagement score = (page_views * 0.3) + (time_on_page * 0.4) + (events_triggered * 0.3)
        """
        query = """
        WITH engagement_scores AS (
            SELECT 
                user_id,
                session_id,
                page_views,
                time_on_page,
                events_triggered,
                (page_views * 0.3 + time_on_page * 0.4 + events_triggered * 0.3) AS engagement_score,
                converted,
                revenue
            FROM user_events
        ),
        percentiles AS (
            SELECT 
                quantile_cont(engagement_score, 0.33) AS p33,
                quantile_cont(engagement_score, 0.67) AS p67
            FROM engagement_scores
        )
        SELECT 
            CASE 
                WHEN e.engagement_score <= p.p33 THEN 'Low'
                WHEN e.engagement_score <= p.p67 THEN 'Medium'
                ELSE 'High'
            END AS engagement_segment,
            COUNT(DISTINCT e.user_id) AS unique_users,
            COUNT(*) AS total_sessions,
            ROUND(AVG(e.page_views), 2) AS avg_page_views,
            ROUND(AVG(e.time_on_page), 2) AS avg_time_on_page,
            ROUND(AVG(e.events_triggered), 2) AS avg_events,
            ROUND(AVG(e.engagement_score), 2) AS avg_engagement_score,
            SUM(CAST(e.converted AS INTEGER)) AS conversions,
            ROUND(AVG(CAST(e.converted AS FLOAT)) * 100, 2) AS conversion_rate,
            ROUND(SUM(e.revenue), 2) AS total_revenue
        FROM engagement_scores e
        CROSS JOIN percentiles p
        GROUP BY engagement_segment
        ORDER BY 
            CASE engagement_segment
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END;
        """
        
        return self.conn.execute(query).df()
    
    def get_user_type_breakdown(self) -> pd.DataFrame:
        """
        Analyze metrics by user type (new vs returning).
        """
        query = """
        SELECT 
            CASE 
                WHEN is_returning THEN 'Returning'
                ELSE 'New'
            END AS user_type,
            COUNT(DISTINCT user_id) AS unique_users,
            COUNT(*) AS total_sessions,
            ROUND(AVG(page_views), 2) AS avg_page_views,
            ROUND(AVG(time_on_page), 2) AS avg_time_on_page,
            ROUND(AVG(events_triggered), 2) AS avg_events,
            SUM(CAST(converted AS INTEGER)) AS conversions,
            ROUND(AVG(CAST(converted AS FLOAT)) * 100, 2) AS conversion_rate,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue_per_session
        FROM user_events
        GROUP BY user_type
        ORDER BY user_type DESC;
        """
        
        return self.conn.execute(query).df()
    
    def get_category_performance(self) -> pd.DataFrame:
        """
        Analyze performance metrics by product category.
        """
        query = """
        SELECT 
            category,
            COUNT(DISTINCT user_id) AS unique_users,
            COUNT(*) AS total_sessions,
            ROUND(AVG(page_views), 2) AS avg_page_views,
            ROUND(AVG(time_on_page), 2) AS avg_time_on_page,
            ROUND(AVG(events_triggered), 2) AS avg_events,
            SUM(CAST(converted AS INTEGER)) AS conversions,
            ROUND(AVG(CAST(converted AS FLOAT)) * 100, 2) AS conversion_rate,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue_per_session,
            ROUND(SUM(revenue) / NULLIF(SUM(CAST(converted AS INTEGER)), 0), 2) AS avg_order_value
        FROM user_events
        GROUP BY category
        ORDER BY total_revenue DESC;
        """
        
        return self.conn.execute(query).df()
    
    def get_timeseries_conversion(self, granularity: str = 'day') -> pd.DataFrame:
        """
        Get time-series conversion data.
        
        Args:
            granularity: 'day', 'week', or 'month'
        """
        date_trunc = {
            'day': 'day',
            'week': 'week',
            'month': 'month'
        }.get(granularity, 'day')
        
        query = f"""
        SELECT 
            date_trunc('{date_trunc}', session_date) AS period,
            COUNT(*) AS total_sessions,
            COUNT(DISTINCT user_id) AS unique_users,
            SUM(CAST(converted AS INTEGER)) AS conversions,
            ROUND(AVG(CAST(converted AS FLOAT)) * 100, 2) AS conversion_rate,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(page_views), 2) AS avg_page_views,
            ROUND(AVG(time_on_page), 2) AS avg_time_on_page,
            SUM(CASE WHEN is_returning THEN 1 ELSE 0 END) AS returning_sessions,
            SUM(CASE WHEN NOT is_returning THEN 1 ELSE 0 END) AS new_sessions
        FROM user_events
        GROUP BY period
        ORDER BY period;
        """
        
        return self.conn.execute(query).df()
    
    def get_conversion_funnel(self) -> pd.DataFrame:
        """
        Analyze conversion funnel stages with proper funnel progression.
        """
        query = """
        WITH funnel_stages AS (
            SELECT 
                CASE 
                    WHEN converted = true THEN 'Converted'
                    WHEN time_on_page > 100 AND events_triggered > 0 AND page_views > 1 THEN 'High Engagement'
                    WHEN events_triggered > 0 AND page_views > 1 THEN 'With Events'
                    WHEN page_views > 1 THEN 'With Page Views'
                    ELSE 'All Sessions'
                END AS funnel_stage,
                COUNT(*) AS sessions,
                SUM(CAST(converted AS INTEGER)) AS conversions,
                SUM(revenue) AS revenue
            FROM user_events
            GROUP BY funnel_stage
        )
        SELECT 
            funnel_stage,
            sessions,
            ROUND((conversions::FLOAT / sessions) * 100, 2) AS conversion_rate,
            ROUND(revenue, 2) AS revenue
        FROM funnel_stages
        ORDER BY 
            CASE funnel_stage
                WHEN 'All Sessions' THEN 1
                WHEN 'With Page Views' THEN 2
                WHEN 'With Events' THEN 3
                WHEN 'High Engagement' THEN 4
                WHEN 'Converted' THEN 5
            END;
        """
        
        return self.conn.execute(query).df()
    
    def get_cohort_analysis(self) -> pd.DataFrame:
        """
        Perform cohort analysis based on first session date.
        """
        query = """
        WITH user_first_session AS (
            SELECT 
                user_id,
                MIN(session_date) AS cohort_date
            FROM user_events
            GROUP BY user_id
        ),
        cohort_data AS (
            SELECT 
                date_trunc('month', ufs.cohort_date) AS cohort_month,
                ue.session_date,
                COUNT(DISTINCT ue.user_id) AS active_users,
                SUM(CAST(ue.converted AS INTEGER)) AS conversions,
                ROUND(SUM(ue.revenue), 2) AS revenue
            FROM user_events ue
            JOIN user_first_session ufs ON ue.user_id = ufs.user_id
            GROUP BY cohort_month, ue.session_date
        )
        SELECT 
            cohort_month,
            COUNT(DISTINCT session_date) AS days_active,
            SUM(active_users) AS total_active_users,
            SUM(conversions) AS total_conversions,
            ROUND(AVG(CAST(conversions AS FLOAT) / NULLIF(active_users, 0)) * 100, 2) AS avg_conversion_rate,
            SUM(revenue) AS total_revenue
        FROM cohort_data
        GROUP BY cohort_month
        ORDER BY cohort_month;
        """
        
        return self.conn.execute(query).df()
    
    def execute_custom_query(self, query: str) -> pd.DataFrame:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        return self.conn.execute(query).df()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
        print("✓ Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Initialize manager
    db = DuckDBManager(":memory:")
    
    # Create tables
    db.create_tables()
    
    # Load data (replace with your CSV path)
    db.load_csv_data("user_events.csv")
    
    # Run analytics queries
    print("\n=== Engagement Segmentation ===")
    print(db.get_engagement_segmentation())
    
    print("\n=== User Type Breakdown ===")
    print(db.get_user_type_breakdown())
    
    print("\n=== Category Performance ===")
    print(db.get_category_performance())
    
    print("\n=== Time-Series Conversions (Daily) ===")
    print(db.get_timeseries_conversion(granularity='day'))
    
    print("\n=== Conversion Funnel ===")
    print(db.get_conversion_funnel())
    
    # Close connection
    db.close()