import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Ola Ride Insights", layout="wide")

# --- 2. DATA LOADING (MySQL with CSV Fallback) ---
@st.cache_data
def load_data():
    try:
        # REPLACE 'your_password' with your actual MySQL password
        engine = create_engine(
            'mysql+mysqlconnector://root:rakesh746348@localhost/ola_db',
            connect_args={'connect_timeout': 5}
        )
        query = "SELECT * FROM rides"
        df_sql = pd.read_sql(query, con=engine)
        return df_sql, "Live MySQL Database"
    except Exception:
        if os.path.exists("ola_dataset.csv"):
            return pd.read_csv("ola_dataset.csv"), "Static CSV File (Cloud Mode)"
        else:
            return None, "Error: No Data Source Found"

df, source_info = load_data()

# --- 3. SIDEBAR: REQUIREMENT 2 (INTERACTIVE FILTERS & SEARCH) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/0/0f/Ola_Cabs_logo.svg", width=100)
st.sidebar.title("Ola Analytics Hub")

st.sidebar.subheader("Filters & Search")
# Filter 1: Search Box
search_id = st.sidebar.text_input("🔍 Search Customer ID:", placeholder="e.g., CID123")

# Filter 2: Interactive Dropdown
if df is not None:
    v_filter = st.sidebar.selectbox("🚗 Filter by Vehicle Type:", ["All"] + list(df['Vehicle_Type'].unique()))
else:
    v_filter = "All"

st.sidebar.markdown("---")
st.sidebar.info(f"**Data Source:** {source_info}")

page = st.sidebar.radio("Navigation", ["Visual Dashboard Gallery", "SQL Data Explorer"])

# --- 4. PAGE CONTENT ---

if df is not None:
    # --- REQUIREMENT 3: EMBED POWER BI VISUALS (COMPLETE ANALYTICS EXPERIENCE) ---
    if page == "Visual Dashboard Gallery":
        st.title("📊 Power BI Executive Insights")
        st.write("Switch between the 5 main dashboard pages to see visual trends.")
        
        view = st.selectbox("Select Dashboard View:", 
                            ["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"])
        
        image_map = {"Overall": "p1.png", "Vehicle Type": "p2.png", "Revenue": "p3.png", "Cancellation": "p4.png", "Ratings": "p5.png"}
        img_file = image_map[view]
        
        if os.path.exists(img_file):
            st.image(img_file, use_container_width=True)
        else:
            st.error(f"Image '{img_file}' not found. Ensure screenshots are in your GitHub repository.")

    # --- REQUIREMENT 1: USER-FRIENDLY UI FOR SQL RESULTS ---
    elif page == "SQL Data Explorer":
        st.title("🔍 SQL Insight Explorer")
        
        # Applying the Interactive Filters from Sidebar
        filtered_df = df.copy()
        if search_id:
            filtered_df = filtered_df[filtered_df['Customer_ID'].astype(str).str.contains(search_id, case=False)]
        if v_filter != "All":
            filtered_df = filtered_df[filtered_df['Vehicle_Type'] == v_filter]

        # UI Enhancement: Key Metrics Cards (This makes it "User Friendly")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Rides Found", len(filtered_df))
        m2.metric("Avg. Booking Value", f"₹{filtered_df['Booking_Value'].mean():.2f}")
        m3.metric("Success Rate", f"{(len(filtered_df[filtered_df['Booking_Status']=='Success'])/len(filtered_df)*100):.1f}%")
        
        st.markdown("---")
        
        # Displaying the Data Table
        st.subheader(f"Data Table: {v_filter} Vehicles")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Add a Download Button as an extra "User-Friendly" touch
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", data=csv, file_name="Ola_results.csv", mime="text/csv")

else:
    st.error("⚠️ Critical Error: Data Source Missing.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Developed for OLA Ride Insights Project | 2026")