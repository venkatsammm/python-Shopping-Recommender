import streamlit as st
import bcrypt
from recommender import get_recommendations
from db_utils import fetch_all_products, create_user, get_user_by_email,get_user_by_username

# ------------- Session State -------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'page' not in st.session_state:
    st.session_state.page = "signup"

# ------------- Custom CSS -------------
st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa, #e4e9f2);
            padding: 0;
        }
        .auth-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .auth-card {
            background-color: white;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .auth-header {
            background: linear-gradient(90deg, #6a11cb, #2575fc);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .auth-form {
            padding: 2rem;
        }
        .form-row {
            display: flex;
            gap: 1rem;
        }
        .auth-footer {
            text-align: center;
            margin-top: 1.5rem;
            padding: 1rem;
            border-top: 1px solid #f0f0f0;
        }
        .toggle-link {
            cursor: pointer;
            color: #2575fc;
            text-decoration: underline;
        }
        .stButton>button {
            background: linear-gradient(90deg, #6a11cb, #2575fc);
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.75em 2em;
            font-size: 16px;
            width: 100%;
            border: none;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            border-radius: 10px !important;
            border: 1px solid #e0e0e0;
            padding: 10px;
        }
        .field-icon {
            font-size: 1.2rem;
            color: #6a11cb;
            margin-right: 8px;
        }
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def toggle_page():
    st.session_state.page = "login" if st.session_state.page == "signup" else "signup"

# ------------- Recommender -------------
def recommender():
    st.title("🛍️ Smart Product Recommender")
    st.markdown(f"Hello, **{st.session_state.user_email}**! Let's find something you'll love ✨")
    
    products = fetch_all_products()
    if not products:
        st.warning("⚠️ No products available right now.")
        return
    
    product_names = [prod['name'] for prod in products]
    selected_product = st.selectbox("🔍 Choose a product:", product_names)
    
    if selected_product:
        recommendations = get_recommendations(selected_product)
        st.subheader("🎯 You Might Also Like:")
        
        # Create columns for a better layout
        for item in recommendations:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(item['image_url'], width=150)
            
            with col2:
                st.markdown(f"**{item['name']}**")
                
                # Display gender with an appropriate emoji
                gender_emoji = "👤"
                if item.get('gender') == 'Male':
                    gender_emoji = "👨"
                elif item.get('gender') == 'Female':
                    gender_emoji = "👩"
                elif item.get('gender') == 'Unisex':
                    gender_emoji = "👫"
                    
                st.markdown(f"*Category:* {item['category']} | {gender_emoji} *Gender:* {item.get('gender', 'Unspecified')}")
                st.markdown(f"{item['description'][:150]}...")
            
            st.markdown("---")
    
# ------------- Sign Up -------------

def signup_page():
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        # Header
        st.markdown('<div class="auth-header">', unsafe_allow_html=True)
        st.title("✨ Create Your Account")
        st.markdown("Join our community and discover personalized product recommendations")
        st.markdown('</div>', unsafe_allow_html=True)

        # Form section
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<p><span class="field-icon">👤</span> Username</p>', unsafe_allow_html=True)
            username = st.text_input("Username", label_visibility="collapsed")

            st.markdown('<p><span class="field-icon">⚧️</span> Gender</p>', unsafe_allow_html=True)
            gender = st.selectbox(
                "Gender",
                ["Select your gender", "Male", "Female"],
                label_visibility="collapsed"
            )

        with col2:
            st.markdown('<p><span class="field-icon">📧</span> Email</p>', unsafe_allow_html=True)
            email = st.text_input("Email", label_visibility="collapsed")

            st.markdown('<p><span class="field-icon">📱</span> Phone (optional)</p>', unsafe_allow_html=True)
            phone = st.text_input("Phone", label_visibility="collapsed")

        st.markdown('<p><span class="field-icon">🔒</span> Password</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", label_visibility="collapsed")

        st.markdown('<p><span class="field-icon">🔁</span> Confirm Password</p>', unsafe_allow_html=True)
        confirm = st.text_input("Confirm Password", type="password", label_visibility="collapsed")

        # Terms of Service
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

        # Sign Up Button Logic
        if st.button("Sign Up"):
            if not username or not email or not password or not confirm:
                st.error("Please fill out all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif gender == "Select your gender":
                st.error("Please select your gender.")
            elif not agree:
                st.error("You must agree to the Terms of Service.")
            elif get_user_by_email(email):
                st.warning("Email already registered. Try logging in.")
            elif get_user_by_username(username):
                st.warning("Username already taken. Please choose a different one.")
            else:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                create_user(username, email, hashed, gender.lower())
                st.success("🎉 Account created successfully! Please sign in.")
                st.session_state.page = "login"
                st.rerun()

        # Footer with login redirection
        st.markdown('<div class="auth-footer">', unsafe_allow_html=True)

        
        if st.button("Go to Login", key="goto_login"):
            st.session_state.page = "login"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-footer
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-form
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-card
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-container


# ------------- Sign In -------------
def login_page():
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<div class="auth-header">', unsafe_allow_html=True)
        st.title("👋 Welcome Back")
        st.markdown("Sign in to continue your journey")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Form
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        
        st.markdown('<p><span class="field-icon">📧</span> Email</p>', unsafe_allow_html=True)
        email = st.text_input("Email", label_visibility="collapsed")
        
        st.markdown('<p><span class="field-icon">🔒</span> Password</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", label_visibility="collapsed")
        
      
        # Submit button
        if st.button("Sign In"):
            user = get_user_by_email(email)
            if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success(f"Welcome back, {user['username']}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        
        # Footer with toggle link
        st.markdown('<div class="auth-footer">', unsafe_allow_html=True)
        if st.button("Go to Signup", key="goto_signup"):
            st.session_state.page = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-form
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-card
        st.markdown('</div>', unsafe_allow_html=True)  # Close auth-container

# ------------- Main Control -------------
def main():
    if st.session_state.authenticated:
        recommender()
    else:
        if st.session_state.page == "signup":
            signup_page()
        else:
            login_page()

if __name__ == "__main__":
    main() 