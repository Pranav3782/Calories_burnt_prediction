import os
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# Create sample data with realistic relationships
n_samples = 1000

# Generate base features
data = {
    'Gender': np.random.choice([0, 1], size=n_samples),  # 0 for male, 1 for female
    'Age': np.random.randint(15, 80, size=n_samples),
    'Height': np.random.uniform(150, 200, size=n_samples),
    'Weight': np.random.uniform(40, 120, size=n_samples),
    'Duration': np.random.uniform(1, 120, size=n_samples),
    'Heart_Rate': np.random.uniform(60, 200, size=n_samples),
    'Body_Temp': np.random.uniform(36, 40, size=n_samples)
}

df = pd.DataFrame(data)

# Calculate calories with realistic relationships
base_calories = np.zeros(n_samples)

# Duration effect (strong positive correlation)
base_calories += df['Duration'] * 5  # ~5 calories per minute base rate

# Heart Rate effect (higher heart rate = more calories)
heart_rate_factor = (df['Heart_Rate'] - 60) / 140  # normalize to 0-1 range
base_calories += heart_rate_factor * df['Duration'] * 3

# Weight effect (heavier people burn more calories)
weight_factor = (df['Weight'] - 40) / 80  # normalize to 0-1 range
base_calories += weight_factor * df['Duration'] * 2

# Age effect (metabolism decreases with age)
age_factor = 1 - (df['Age'] - 15) / 65  # normalize to 1-0 range (younger = higher metabolism)
base_calories *= (0.7 + 0.3 * age_factor)  # age affects 30% of calorie burn

# Gender effect (males typically burn slightly more calories)
gender_factor = np.where(df['Gender'] == 0, 1.1, 0.9)  # 10% difference between males and females
base_calories *= gender_factor

# Body temperature effect (higher temperature indicates more intense workout)
temp_factor = (df['Body_Temp'] - 36) / 4  # normalize to 0-1 range
base_calories *= (1 + 0.2 * temp_factor)  # temperature affects up to 20% of calorie burn

# Add some random variation (±10%)
random_factor = np.random.uniform(0.9, 1.1, size=n_samples)
base_calories *= random_factor

# Ensure calories are positive and within reasonable range
df['Calories'] = np.clip(base_calories, 50, 1000)

# Prepare features and target
X = df.drop('Calories', axis=1)
Y = df['Calories']

# Split the data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=2)

# Train the model
model = XGBRegressor()
model.fit(X_train, Y_train)

# Save the model
current_dir = os.path.dirname(os.path.abspath(__file__))
model.save_model(os.path.join(current_dir, "calories_model.json"))
