# app_phase2.py
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import sqlite3
import hashlib

# ================= DATABASE SETUP =================
conn = sqlite3.connect('students.db')
c = conn.cursor()

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
''')
# CGPA table
c.execute('''
CREATE TABLE IF NOT EXISTS cgpa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    course TEXT,
    unit INTEGER,
    score INTEGER
)
''')
conn.commit()

# ================= FUNCTIONS =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name,email,hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    data = c.fetchone()
    return data  # Returns user row if exists

# =================== APP CONFIG ===================
st.set_page_config(page_title="🎓 Student Helper App", page_icon="🎯", layout="wide")

# =================== LOGIN / REGISTER ===================
st.sidebar.title("👤 Login/Register")
auth_action = st.sidebar.radio("Action:", ["Login","Register"])

if auth_action == "Register":
    st.sidebar.subheader("Create Account")
    reg_name = st.sidebar.text_input("Full Name")
    reg_email = st.sidebar.text_input("Email")
    reg_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Register"):
        if register_user(reg_name, reg_email, reg_password):
            st.success("✅ Account created! Please login.")
        else:
            st.error("❌ Email already exists!")

else:  # Login
    st.sidebar.subheader("Login")
    login_email = st.sidebar.text_input("Email")
    login_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = login_user(login_email, login_password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user[1]} 🎉")
        else:
            st.error("❌ Invalid email or password")

# =================== MAIN APP AFTER LOGIN ===================
if 'user' in st.session_state:
    st.sidebar.title("📚 Modules")
    module = st.sidebar.radio("Select Module:", ["Score Predictor","CGPA Calculator","Project Helper (Coming Soon)","Practice Questions (Coming Soon)","Resource Sharing (Coming Soon)"])

    # ---------------- SCORE PREDICTOR ----------------
    if module == "Score Predictor":
        st.title("🎯 Student Score Predictor")
        st.write("Predict your expected score based on hours studied!")

        # Sample data
        data = {'Hours_Studied':[10,20,30,40,50,60,70,80,90,120], 'Scores':[30,35,40,50,55,60,65,70,80,95]}
        df = pd.DataFrame(data)
        X = df[['Hours_Studied']]
        y = df['Scores']
        model = LinearRegression()
        model.fit(X, y)

        col1, col2 = st.columns([1,1])
        with col1:
            hours = st.slider("Select hours studied:", 0, 12, 5)
            if st.button("Predict Score"):
                prediction = model.predict([[hours]])
                st.success(f"🎉 Predicted Score: {prediction[0]:.2f}")

        with col2:
            st.subheader("📊 Performance Graph")
            plt.figure(figsize=(5,4))
            plt.scatter(df['Hours_Studied'], df['Scores'], color='orange')
            plt.plot(df['Hours_Studied'], model.predict(X), color='green')
            plt.xlabel("Hours Studied")
            plt.ylabel("Scores")
            plt.grid(True)
            st.pyplot(plt)

    # ---------------- CGPA CALCULATOR ----------------
    elif module == "CGPA Calculator":
        st.title("🎓 CGPA Calculator")
        st.write("Calculate your CGPA for University or Polytechnic!")

        institution = st.selectbox("Select Institution Type:", ["University","Polytechnic","College"])
        
        if 'courses' not in st.session_state:
            st.session_state.courses = pd.DataFrame(columns=['Course','Unit','Score'])

        col1, col2 = st.columns([2,1])
        with col1:
            course_name = st.text_input("Course Code (e.g., MTH101)")
            course_unit = st.number_input("Course Unit:", min_value=1,max_value=10,step=1)
            course_score = st.number_input("Score/Grade:", min_value=0,max_value=100,step=1)
            if st.button("Add Course"):
                if course_name:
                    new_row = pd.DataFrame({'Course':[course_name],'Unit':[course_unit],'Score':[course_score]})
                    st.session_state.courses = pd.concat([st.session_state.courses,new_row],ignore_index=True)
                    # Save to DB
                    c.execute("INSERT INTO cgpa_history (user_id,course,unit,score) VALUES (?,?,?,?)",
                              (st.session_state.user[0], course_name, course_unit, course_score))
                    conn.commit()
                    st.success(f"Added {course_name} ✅")

        with col2:
            st.subheader("📋 Courses Table")
            if st.session_state.courses.empty:
                st.info("No courses added yet.")
            else:
                st.table(st.session_state.courses)

        # Calculate CGPA
        def get_grade_point(score, institution):
            if institution=="University":
                if score>=70: return 5
                elif score>=60: return 4
                elif score>=50: return 3
                elif score>=45: return 2
                elif score>=40: return 1
                else: return 0
            else:
                if score>=70: return 4
                elif score>=60: return 3
                elif score>=50: return 2
                elif score>=45: return 1
                else: return 0

        if not st.session_state.courses.empty:
            df = st.session_state.courses.copy()
            df['Grade Point'] = df['Score'].apply(lambda x: get_grade_point(x,institution))
            df['Weighted'] = df['Unit'] * df['Grade Point']
            cgpa = df['Weighted'].sum()/df['Unit'].sum()
            st.success(f"🎉 Your CGPA is: {cgpa:.2f}")
            st.bar_chart(df[['Course','Grade Point']].set_index('Course'))

    # ---------------- OTHER MODULES PLACEHOLDERS ----------------
    else:
        st.title(module)
        st.info("Coming Soon! Phase 2 modules (Project Helper, Practice Questions, Resource Sharing) will be implemented here.")

else:
    st.warning("Please login or register to access the app 🔐")
