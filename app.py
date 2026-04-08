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
import streamlit as st
import pandas as pd

st.title("🎓 Student CGPA Calculator")

# Select Institution Type
institution = st.selectbox("Select Institution Type:", ["University", "Polytechnic"])

st.write("Enter your courses below:")

# Create empty dataframe for courses
if 'courses' not in st.session_state:
    st.session_state.courses = pd.DataFrame(columns=['Course', 'Unit', 'Score'])

# Input course
course_name = st.text_input("Course Code (e.g., MTH101)")
course_unit = st.number_input("Course Unit:", min_value=1, max_value=10, step=1)
course_score = st.number_input("Score/Grade:", min_value=0, max_value=100, step=1)

if st.button("Add Course"):
    if course_name:
        new_row = pd.DataFrame({'Course':[course_name], 'Unit':[course_unit], 'Score':[course_score]})
        st.session_state.courses = pd.concat([st.session_state.courses, new_row], ignore_index=True)
        st.success(f"Added {course_name}.")

# Display table
st.subheader("Your Courses")
st.table(st.session_state.courses)

# Calculate CGPA
def get_grade_point(score, institution):
    if institution == "University":
        if score >= 70: return 5
        elif score >= 60: return 4
        elif score >= 50: return 3
        elif score >= 45: return 2
        elif score >= 40: return 1
        else: return 0
    else:  # Polytechnic
        if score >= 70: return 4
        elif score >= 60: return 3
        elif score >= 50: return 2
        elif score >= 45: return 1
        else: return 0

if not st.session_state.courses.empty:
    st.subheader("CGPA Result")
    df = st.session_state.courses
    df['Grade Point'] = df['Score'].apply(lambda x: get_grade_point(x, institution))
    df['Weighted'] = df['Unit'] * df['Grade Point']
    cgpa = df['Weighted'].sum() / df['Unit'].sum()
    st.success(f"Your CGPA is: {cgpa:.2f}")
