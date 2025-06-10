import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configure Gemini - REPLACE WITH YOUR ACTUAL API KEY
YOUR_API_KEY = "AIzaSyAgEitj_uAy5UpNmxNl5RX8Sdh6BAQw0C4"  # Replace this with your real API key
genai.configure(api_key=YOUR_API_KEY)

# Navigation bar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Meal Planner", "Progress Tracker"])

# App title
st.title("🍽️ Simple Meal Plan Generator")
st.write("Practice version - no secrets.toml needed")

if page == "Meal Planner":
    # User inputs
    with st.expander("Dietary Preferences", expanded=True):
        dietary_pref = st.multiselect(
            "Select dietary preferences",
            ["Vegan", "Vegetarian", "Keto", "Gluten-free", "Low-carb", "Dairy-free"]
        )
        allergies = st.text_input("Any allergies? (e.g., nuts, shellfish)")
        health_goal = st.selectbox(
            "Health Goal",
            ["Weight loss", "Muscle gain", "Maintenance", "General health"]
        )
        cooking_time = st.select_slider(
            "Daily cooking time",
            options=["<30 min", "30-60 min", "1-2 hours", "Quick meals only"]
        )

    # Generate meal plan
    if st.button("Generate Meal Plan"):
        with st.spinner("Creating your personalized meal plan..."):
            prompt = f"""
            Create a 3-day detailed meal plan with:
            - Dietary preferences: {', '.join(dietary_pref) if dietary_pref else 'No restrictions'}
            - Allergies: {allergies if allergies else 'None'}
            - Health goal: {health_goal}
            - Cooking time: {cooking_time}
            
            For each day include:
            1. Breakfast (with ingredients and simple instructions)
            2. Lunch (with ingredients and simple instructions)
            3. Dinner (with ingredients and simple instructions)
            4. One healthy snack suggestion
            
            Format as markdown with clear day headings (## Day 1, etc.).
            Include approximate preparation times for each meal.
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
                # Add a download button
                st.download_button(
                    label="Download Meal Plan",
                    data=response.text,
                    file_name=f"meal_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error generating meal plan: {e}")
                st.info("Make sure you: \n1. Replaced the API key \n2. Have internet access \n3. Have valid API credentials")

elif page == "Progress Tracker":
    st.header("📊 Your Progress Tracker")
    
    # Initialize session state for weight tracking
    if 'weight_data' not in st.session_state:
        st.session_state.weight_data = pd.DataFrame(columns=["Date", "Weight"])
    
    # Weight input form
    with st.form("weight_form"):
        st.subheader("Add New Measurement")
        date = st.date_input("Date")
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
        submitted = st.form_submit_button("Save")
        
        if submitted:
            new_entry = pd.DataFrame([[date, weight]], columns=["Date", "Weight"])
            st.session_state.weight_data = pd.concat([st.session_state.weight_data, new_entry])
            st.success("Measurement saved!")
    
    # Display progress chart
    if not st.session_state.weight_data.empty:
        st.subheader("Weight Progress")
        fig, ax = plt.subplots()
        st.session_state.weight_data = st.session_state.weight_data.sort_values("Date")
        ax.plot(st.session_state.weight_data["Date"], st.session_state.weight_data["Weight"], marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (kg)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Show data table
        st.dataframe(st.session_state.weight_data.sort_values("Date", ascending=False))
    else:
        st.info("No weight data yet. Add your first measurement above.")

# Disclaimer
st.warning("Note: This is a practice version. For real projects, never hardcode API keys.")