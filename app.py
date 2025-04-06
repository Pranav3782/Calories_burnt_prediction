import streamlit as st
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import pickle

# Set page config
st.set_page_config(page_title="Calories Burnt Prediction", page_icon="")

# Title and description
st.title("Calories Burnt Prediction")
st.write("Enter your details to predict calories burnt during exercise")

# Create the input form
with st.form("prediction_form"):
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.selectbox("Gender", ["male", "female"])
        age = st.number_input("Age", min_value=15, max_value=80, value=25)
        height = st.number_input("Height (cm)", min_value=130, max_value=250, value=170)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=30)
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=60, max_value=200, value=110)
        body_temp = st.number_input("Body Temperature (°C)", min_value=35.0, max_value=41.0, value=37.0, step=0.1)
    
    submit_button = st.form_submit_button("Predict Calories")

# Load the model
@st.cache_resource
def load_model():
    model = XGBRegressor()
    model.load_model("calories_model.json")
    return model

# When form is submitted
if submit_button:
    try:
        # Load the model
        model = load_model()
        
        # Prepare input data
        input_data = pd.DataFrame({
            'Gender': [0 if gender == 'male' else 1],
            'Age': [age],
            'Height': [height],
            'Weight': [weight],
            'Duration': [duration],
            'Heart_Rate': [heart_rate],
            'Body_Temp': [body_temp]
        })
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Display result
        st.success(f"Predicted Calories Burnt: {prediction:.0f} calories")
        
        # Display insights
        st.subheader("Workout Analysis")
        
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        # Duration Impact
        with col1:
            calories_per_min = prediction / duration
            st.metric("Calories/Minute", f"{calories_per_min:.1f}")
        
        # Heart Rate Zone
        with col2:
            max_hr = 220 - age
            hr_percentage = (heart_rate / max_hr) * 100
            hr_zone = "Low" if hr_percentage < 60 else "Moderate" if hr_percentage < 75 else "High"
            st.metric("Heart Rate Zone", hr_zone)
        
        # Workout Intensity
        with col3:
            if prediction < 200:
                intensity = "Light"
            elif prediction < 400:
                intensity = "Moderate"
            else:
                intensity = "High"
            st.metric("Workout Intensity", intensity)
        
        # Factors affecting calorie burn
        st.subheader("Factors Affecting Your Calorie Burn")
        factors = []
        
        # Duration factor
        factors.append(f"• Duration ({duration} mins): {'High' if duration > 45 else 'Moderate' if duration > 20 else 'Low'} impact")
        
        # Heart rate factor
        factors.append(f"• Heart Rate ({heart_rate} bpm): {'High' if hr_percentage > 75 else 'Moderate' if hr_percentage > 60 else 'Low'} impact")
        
        # Weight factor
        weight_impact = "High" if weight > 80 else "Moderate" if weight > 60 else "Low"
        factors.append(f"• Weight ({weight} kg): {weight_impact} impact")
        
        # Age factor
        age_impact = "High" if age < 30 else "Moderate" if age < 50 else "Low"
        factors.append(f"• Age ({age} years): {age_impact} metabolic rate")
        
        # Display factors
        for factor in factors:
            st.write(factor)
        
        # Tips based on the workout
        st.subheader("Tips for Your Workout")
        if duration < 20:
            st.info("Consider increasing your workout duration for better calorie burn")
        if hr_percentage < 60:
            st.info("Try to increase your heart rate to achieve better results")
        if body_temp < 37:
            st.info("Your body temperature indicates low workout intensity")
            
    except Exception as e:
        st.error("Error occurred while making prediction. Please make sure the model file exists and all inputs are valid.")
