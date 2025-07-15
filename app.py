import streamlit as st
import pymongo
from pymongo import MongoClient
import pandas as pd

# MongoDB connection
@st.cache_resource
def init_connection():
    try:
        client = MongoClient("mongodb+srv://testdb:dbUsername@cluster.di9pq.mongodb.net/")
        return client
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

@st.cache_data
def load_data():
    client = init_connection()
    if client is None:
        return pd.DataFrame()
    
    try:
        db = client.hotels
        collection = db.hotel_list
        
        # Fetch all hotels
        hotels = list(collection.find({}, {"_id": 0}))
        
        if hotels:
            return pd.DataFrame(hotels)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def main():
    st.set_page_config(
        page_title="Hotel Finder",
        page_icon="🏨",
        layout="wide"
    )
    
    st.title("🏨 Hotel Finder")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No hotel data found or unable to connect to database.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get unique values for filters
    unique_places = sorted(df['place'].unique()) if 'place' in df.columns else []
    unique_states = sorted(df['state'].unique()) if 'state' in df.columns else []
    
    # Place filter
    selected_places = st.sidebar.multiselect(
        "Select Place(s):",
        options=unique_places,
        default=unique_places
    )
    
    # State filter
    selected_states = st.sidebar.multiselect(
        "Select State(s):",
        options=unique_states,
        default=unique_states
    )
    
    # Rating filter
    if 'rating' in df.columns:
        min_rating = float(df['rating'].min())
        max_rating = float(df['rating'].max())
        
        rating_range = st.sidebar.slider(
            "Rating Range:",
            min_value=min_rating,
            max_value=max_rating,
            value=(min_rating, max_rating),
            step=0.1
        )
    else:
        rating_range = (0, 5)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_places:
        filtered_df = filtered_df[filtered_df['place'].isin(selected_places)]
    
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    
    if 'rating' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['rating'] >= rating_range[0]) & 
            (filtered_df['rating'] <= rating_range[1])
        ]
    
    # Display results
    st.header(f"Found {len(filtered_df)} hotel(s)")
    
    if filtered_df.empty:
        st.info("No hotels match the selected filters.")
        return
    
    # Display hotels one by one
    for idx, hotel in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.subheader(hotel.get('name', 'Unknown Hotel'))
            
            with col2:
                rating = hotel.get('rating', 'N/A')
                if isinstance(rating, (int, float)):
                    st.metric("Rating", f"{rating}/5", delta=None)
                else:
                    st.metric("Rating", rating)
            
            with col3:
                st.write(f"📍 **Place:** {hotel.get('place', 'N/A')}")
            
            with col4:
                st.write(f"🏛️ **State:** {hotel.get('state', 'N/A')}")
            
            # Additional details if available
            if 'country' in hotel:
                st.write(f"🌍 **Country:** {hotel.get('country', 'N/A')}")
            
            st.markdown("---")
    
    # Summary statistics
    if not filtered_df.empty:
        st.sidebar.markdown("---")
        st.sidebar.header("Summary")
        st.sidebar.write(f"Total Hotels: {len(filtered_df)}")
        
        if 'rating' in filtered_df.columns:
            avg_rating = filtered_df['rating'].mean()
            st.sidebar.write(f"Average Rating: {avg_rating:.2f}")
        
        if 'place' in filtered_df.columns:
            most_common_place = filtered_df['place'].mode().iloc[0] if not filtered_df['place'].mode().empty else "N/A"
            st.sidebar.write(f"Most Common Place: {most_common_place}")

if __name__ == "__main__":
    main()