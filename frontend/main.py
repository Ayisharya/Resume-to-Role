import streamlit as st
import sqlite3
from dashboard import employee_dashboard
from hr_dashboard import hr_dashboard

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 first_name TEXT NOT NULL,
                 last_name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 phone TEXT,
                 password TEXT NOT NULL,
                 role TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Resume - to - Role", layout="wide")

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None

st.title("Resume - to - Role")

def register_user(first, last, email, phone, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (first_name, last_name, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                  (first, last, email, phone, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error("Email already registered!")
        return False
    finally:
        conn.close()

def authenticate_user(first, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE first_name=? AND password=?", (first, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "first": user[1],
            "last": user[2],
            "email": user[3],
            "phone": user[4],
            "role": user[6]
        }
    return None

if st.session_state.auth_mode is None:
    st.header("Welcome! Please choose an option")
    if st.button("Register"):
        st.session_state.auth_mode = "register"
    if st.button("Sign In"):
        st.session_state.auth_mode = "login"

elif st.session_state.auth_mode == "register":
    st.header(" Register")
    first = st.text_input("First Name", key="reg_first")
    last = st.text_input("Last Name", key="reg_last")
    email = st.text_input("Email", key="reg_email")
    phone = st.text_input("Phone Number", key="reg_phone")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
    
    if st.button("Submit Registration"):
        if not all([first, last, email, password, confirm_password]):
            st.error("Please fill all required fields!")
        elif password != confirm_password:
            st.error("Passwords don't match!")
        else:
            if register_user(first, last, email, phone, password):
                st.success("Registration successful! Please sign in.")
                st.session_state.auth_mode = "login"

elif st.session_state.auth_mode == "login":
    st.header(" Sign In")
    first = st.text_input("First Name", key="login_first")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Sign In"):
        user = authenticate_user(first, password)
        if user:
            st.session_state.user = user
            if user["role"]:
                if user["role"] == "Employee":
                    st.session_state.auth_mode = "employee"
                else:
                    st.session_state.auth_mode = "hr"
            else:
                st.session_state.auth_mode = "role"
            st.rerun()
        else:
            st.error("Invalid credentials!")

elif st.session_state.auth_mode == "role":
    st.header(f"Welcome {st.session_state.user['first']}! Please select your role:")
    role = st.radio("I am a...", ["Employee", "HR"], key="role_select")
    if st.button("Continue"):
        # Update role in database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET role=? WHERE id=?", 
                  (role, st.session_state.user["id"]))
        conn.commit()
        conn.close()
        
        st.session_state.user["role"] = role
        if role == "Employee":
            st.session_state.auth_mode = "employee"
        else:
            st.session_state.auth_mode = "hr"
        st.rerun()

elif st.session_state.auth_mode == "employee":
    employee_dashboard()

elif st.session_state.auth_mode == "hr":
    hr_dashboard()