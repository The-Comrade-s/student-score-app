import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

data = {
    'Hours_Studied': [5,10,15,20,30,40,50,70,90,120],
    'Scores': [25,35,40,45,50,55,60,70,80,95]
}

df = pd.DataFrame(data)

X = df[['Hours_Studied']]
y = df['Scores']

model = LinearRegression()
model.fit(X, y)

st.title("Student Score Predictor")

hours = st.number_input("Enter hours studied:", 0.0, 120.0)

if st.button("Predict"):
    prediction = model.predict([[hours]])
    st.write(f"Predicted Score: {prediction[0]:.2f}")
