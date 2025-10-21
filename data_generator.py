import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_gtm_data(num_sessions=750):
    """
    Generate synthetic GTM event data for user sessions
    
    Parameters:
    num_sessions (int): Number of sessions to generate (default: 750)
    
    Returns:
    pd.DataFrame: Generated synthetic data
    """
    
    # Configuration
    num_users = num_sessions // 3  # Average 3 sessions per user
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    
    data = []
    
    # Generate date range (last 90 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(num_sessions):
        # Generate user_id (some users have multiple sessions)
        user_id = f"user_{random.randint(1, num_users):05d}"
        
        # Session ID (unique for each session)
        session_id = f"session_{i+1:06d}"
        
        # Page views (1-20 pages, with realistic distribution)
        page_views = int(np.random.gamma(2, 2)) + 1
        page_views = min(page_views, 20)
        
        # Time on page (in seconds, 30s to 30 mins)
        time_on_page = int(np.random.exponential(180)) + 30
        time_on_page = min(time_on_page, 1800)
        
        # Events triggered (clicks, scrolls, form submissions, etc.)
        events_triggered = int(np.random.poisson(page_views * 1.5))
        
        # Product category
        category = random.choice(categories)
        
        # Returning user (70% chance if user_id < 70% of total users)
        user_num = int(user_id.split('_')[1])
        is_returning = 1 if user_num < (num_users * 0.4) else random.choices([0, 1], weights=[0.7, 0.3])[0]
        
        # Conversion probability (higher for returning users and more page views)
        conv_prob = 0.05 + (0.1 if is_returning else 0) + (page_views * 0.01)
        conv_prob = min(conv_prob, 0.5)
        converted = 1 if random.random() < conv_prob else 0
        
        # Revenue (only if converted)
        if converted:
            # Revenue varies by category
            category_multipliers = {
                'Electronics': 3.0,
                'Clothing': 1.0,
                'Home & Garden': 2.0,
                'Sports': 1.5,
                'Books': 0.5
            }
            base_revenue = np.random.gamma(2, 30)
            revenue = round(base_revenue * category_multipliers[category], 2)
        else:
            revenue = 0.0
        
        # Random session date within last 90 days
        random_days = random.randint(0, 90)
        session_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Append to data
        data.append({
            'user_id': user_id,
            'session_id': session_id,
            'page_views': page_views,
            'time_on_page': time_on_page,
            'events_triggered': events_triggered,
            'category': category,
            'is_returning': is_returning,
            'converted': converted,
            'revenue': revenue,
            'session_date': session_date
        })
    
    return pd.DataFrame(data)


def clean_and_validate_data(df):
    """
    Clean and validate the generated data
    
    Parameters:
    df (pd.DataFrame): Input dataframe
    
    Returns:
    pd.DataFrame: Cleaned dataframe
    """
    
    print("Original data shape:", df.shape)
    
    # Check for nulls
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\nNull values found:")
        print(null_counts[null_counts > 0])
        df = df.dropna()
    else:
        print("\nNo null values found.")
    
    # Check for duplicates (by session_id)
    duplicates = df.duplicated(subset=['session_id']).sum()
    if duplicates > 0:
        print(f"\n{duplicates} duplicate session_ids found. Removing duplicates...")
        df = df.drop_duplicates(subset=['session_id'], keep='first')
    else:
        print("\nNo duplicate session_ids found.")
    
    # Validate data ranges
    print("\nValidating data ranges...")
    
    # Page views should be positive
    invalid_pv = df[df['page_views'] <= 0].shape[0]
    if invalid_pv > 0:
        print(f"  - Removing {invalid_pv} rows with invalid page_views")
        df = df[df['page_views'] > 0]
    
    # Time on page should be positive
    invalid_time = df[df['time_on_page'] <= 0].shape[0]
    if invalid_time > 0:
        print(f"  - Removing {invalid_time} rows with invalid time_on_page")
        df = df[df['time_on_page'] > 0]
    
    # Events should be non-negative
    invalid_events = df[df['events_triggered'] < 0].shape[0]
    if invalid_events > 0:
        print(f"  - Removing {invalid_events} rows with invalid events_triggered")
        df = df[df['events_triggered'] >= 0]
    
    # Revenue should be non-negative
    invalid_revenue = df[df['revenue'] < 0].shape[0]
    if invalid_revenue > 0:
        print(f"  - Removing {invalid_revenue} rows with invalid revenue")
        df = df[df['revenue'] >= 0]
    
    # Binary columns should be 0 or 1
    df['is_returning'] = df['is_returning'].astype(int).clip(0, 1)
    df['converted'] = df['converted'].astype(int).clip(0, 1)
    
    print("\nCleaned data shape:", df.shape)
    
    return df


def main():
    """
    Main function to generate, clean, and export GTM data
    """
    
    print("=" * 60)
    print("GTM Event Data Generator")
    print("=" * 60)
    
    # Generate synthetic data
    print("\nGenerating synthetic GTM event data...")
    df = generate_gtm_data(num_sessions=750)
    
    # Display sample data
    print("\nSample of generated data:")
    print(df.head(10))
    
    # Clean and validate
    print("\n" + "=" * 60)
    print("Data Cleaning and Validation")
    print("=" * 60)
    df_cleaned = clean_and_validate_data(df)
    
    # Display summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(df_cleaned.describe())
    
    print("\nCategory distribution:")
    print(df_cleaned['category'].value_counts())
    
    print("\nConversion metrics:")
    print(f"  - Total sessions: {len(df_cleaned)}")
    print(f"  - Converted sessions: {df_cleaned['converted'].sum()}")
    print(f"  - Conversion rate: {df_cleaned['converted'].mean()*100:.2f}%")
    print(f"  - Total revenue: ${df_cleaned['revenue'].sum():.2f}")
    print(f"  - Average order value: ${df_cleaned[df_cleaned['converted']==1]['revenue'].mean():.2f}")
    
    # Export to CSV
    output_file = 'gtm_event_data.csv'
    df_cleaned.to_csv(output_file, index=False)
    print(f"\n✓ Data exported to: {output_file}")
    
    return df_cleaned


if __name__ == "__main__":
    df = main()