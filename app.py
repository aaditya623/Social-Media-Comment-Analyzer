import streamlit as st
import requests
import sqlite3
import hashlib

# Set page title and icon
st.set_page_config(page_title="Social Media Comment Analyzer", page_icon="📊")

# Function to set background image dynamically
def set_background(platform):
    background_images = {
        "YouTube": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1280px-YouTube_full-color_icon_%282017%29.svg.png",
        "Instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1024px-Instagram_logo_2016.svg.png",
        "Facebook": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Facebook_f_logo_%282019%29.svg/1024px-Facebook_f_logo_%282019%29.svg.png",
        "X (Twitter)": "https://upload.wikimedia.org/wikipedia/commons/5/57/X_logo_2023_%28white%29.png"
    }
    image_url = background_images.get(platform, "")
    if image_url:
        # Adjust background size based on platform
        background_size = "800px" if platform == "YouTube" else "500px" if platform == "Instagram" else "450px" if platform == "X (Twitter)" else "600px"
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("{image_url}");
                background-size: {background_size};
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                opacity: 0.8; /* Adjust opacity for better readability */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 8px;
    }
    .stTextInput input {
        font-size: 16px;
        padding: 10px;
    }
    .comment-box {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .positive { color: green; }
    .neutral { color: grey; }
    .negative { color: red; }
    .welcome-message {
        font-size: 36px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-top: 20%;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize database
def init_db():
    conn = sqlite3.connect("user_data.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            url TEXT,
            results TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def sign_up(username, password):
    conn = sqlite3.connect("user_data.db", check_same_thread=False)
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def sign_in(username, password):
    conn = sqlite3.connect("user_data.db", check_same_thread=False)
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

# Save analysis results to database
def save_analysis(user_id, platform, url, results):
    conn = sqlite3.connect("user_data.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO analysis_history (user_id, platform, url, results) VALUES (?, ?, ?, ?)",
              (user_id, platform, url, str(results)))
    conn.commit()
    conn.close()

# Retrieve past analysis for a user
def get_past_analysis(user_id):
    conn = sqlite3.connect("user_data.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, platform, url, results FROM analysis_history WHERE user_id = ?", (user_id,))
    analysis = c.fetchall()
    conn.close()
    return analysis

# Initialize database
init_db()

# Session state for user authentication and selected analysis
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = None

# Sign Up and Sign In forms
if st.session_state.user_id is None:
    # Display welcome message
    st.markdown(
        '<div class="welcome-message">Welcome to Social Media Comment Analyzer</div>',
        unsafe_allow_html=True
    )
    st.sidebar.title("Sign Up / Sign In")
    choice = st.sidebar.radio("Choose an option:", ["Sign In", "Sign Up"])

    if choice == "Sign Up":
        st.sidebar.subheader("Create a New Account")
        new_username = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Sign Up"):
            if new_username and new_password:
                if sign_up(new_username, new_password):
                    st.sidebar.success("Account created successfully! Please sign in.")
                else:
                    st.sidebar.error("Username already exists. Please choose a different username.")
            else:
                st.sidebar.warning("Please enter a username and password.")

    elif choice == "Sign In":
        st.sidebar.subheader("Sign In to Your Account")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Sign In"):
            user_id = sign_in(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.sidebar.success("Signed in successfully!")
            else:
                st.sidebar.error("Invalid username or password.")

# Main app functionality
if st.session_state.user_id:
    st.sidebar.title(f"Welcome, User {st.session_state.user_id}")
    if st.sidebar.button("Sign Out"):
        st.session_state.user_id = None
        st.session_state.selected_analysis = None
        st.experimental_rerun()

    # Display past analysis as clickable boxes
    st.sidebar.subheader("Past Analysis")
    past_analysis = get_past_analysis(st.session_state.user_id)
    if past_analysis:
        for analysis in past_analysis:
            analysis_id, platform, url, results = analysis
            if st.sidebar.button(f"{platform} - {url}", key=analysis_id):
                st.session_state.selected_analysis = {
                    "platform": platform,
                    "url": url,
                    "results": eval(results)  # Convert string back to dictionary
                }
                st.experimental_rerun()
    else:
        st.sidebar.write("No past analysis found.")

    # Main app
    st.title("📊 Social Media Comment Analyzer")
    st.write("Analyze comments from YouTube, Instagram, Facebook, or X (Twitter).")

    # Set background based on selected platform
    platform = st.selectbox("Choose a platform:", ["YouTube", "Instagram", "Facebook", "X (Twitter)"])
    set_background(platform)

    # Input for URL
    url = st.text_input(f"Enter the {platform} URL:")

    # Analyze button
    if st.button("Analyze Comments"):
        if url:
            with st.spinner("Analyzing comments..."):
                # Send the URL to the Flask backend
                response = requests.post("http://localhost:5000/analyze", json={"platform": platform, "url": url})
                if response.status_code == 200:
                    results = response.json()
                    st.success("Analysis complete!")

                    # Save analysis to database
                    save_analysis(st.session_state.user_id, platform, url, results)

                    # Display results
                    st.session_state.selected_analysis = {
                        "platform": platform,
                        "url": url,
                        "results": results
                    }
                    st.experimental_rerun()
                else:
                    st.error(response.json().get("error", "Failed to analyze comments. Please check the URL and try again."))
        else:
            st.warning("Please enter a valid URL.")

    # Display selected past analysis
    if st.session_state.selected_analysis:
        st.subheader(f"Analysis for {st.session_state.selected_analysis['platform']} - {st.session_state.selected_analysis['url']}")
        results = st.session_state.selected_analysis["results"]

        # Display comments with sentiment in white boxes
        st.subheader("Top Comments:")
        for comment, sentiment in results.items():
            if sentiment == "positive":
                st.markdown(
                    f'<div class="comment-box"><p class="positive">👍 {comment}</p></div>',
                    unsafe_allow_html=True
                )
            elif sentiment == "neutral":
                st.markdown(
                    f'<div class="comment-box"><p class="neutral">😐 {comment}</p></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="comment-box"><p class="negative">👎 {comment}</p></div>',
                    unsafe_allow_html=True
                )