import streamlit as st
import pdfplumber
import time

# ---- Page Configuration ----
st.set_page_config(page_title="MediBot", layout="wide")

# ---- Custom CSS ----
st.markdown("""
<style>
.chat-title {
    font-size: 2.5em;
    color: #00ffcc;
    text-align: center;
    padding: 20px;
}
.chat-container {
    height: 500px;
    overflow-y: auto;
    padding: 10px;
    background-color: #1e1e1e;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user-msg {
    background-color: #005f73;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    color: white;
}
.bot-msg {
    background-color: #3a3a3a;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    color: white;
}
.footer {
    text-align: center;
    color: #888;
    font-size: 0.8em;
    padding-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---- Session State ----
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# ---- PDF Upload & Extraction ----
uploaded_file = st.sidebar.file_uploader("📄 Upload Medical PDF", type=["pdf"])

def extract_text_from_pdf(file_obj):
    with pdfplumber.open(file_obj) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# ---- Disease Info Retrieval ----
def get_disease_info(query):
    if uploaded_file and not st.session_state.extracted_text:
        with st.spinner('Extracting PDF content...'):
            time.sleep(2)  # Simulate loading time
            st.session_state.extracted_text = extract_text_from_pdf(uploaded_file)
        st.success('PDF content extracted successfully!')

    if not st.session_state.extracted_text:
        return "Please upload a PDF to begin searching."

    extracted_text = st.session_state.extracted_text.lower()
    query = query.lower()

    if query in extracted_text:
        start = extracted_text.find(query)
        end = extracted_text.find(".", start) + 1
        answer = extracted_text[start:end]
    else:
        answer = "Sorry, I couldn't find any medical info about that in the document."

    return answer

# ---- Auth Page ----
def show_auth_page():
    st.markdown("<div class='chat-title'>🔐 MediBot Login</div>", unsafe_allow_html=True)
    choice = st.radio("Choose:", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Submit"):
        if choice == "Signup":
            if len(password) < 8:
                st.warning("Password must be at least 8 characters.")
            elif email in st.session_state.users:
                st.error("Email already registered.")
            else:
                st.session_state.users[email] = password
                st.success("Signup successful! Now login.")
        elif choice == "Login":
            if st.session_state.users.get(email) == password:
                st.success("Login successful!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials.")

# ---- Chat Interface ----
def show_chat():
    # ---- Sidebar: Previous Questions ----
    with st.sidebar:
        st.title("📜 Previous Questions")
        if st.session_state.chat_history:
            for q, _ in reversed(st.session_state.chat_history):
                st.markdown(f"• {q}", unsafe_allow_html=True)
        else:
            st.info("No questions asked yet.")

    st.markdown("<div class='chat-title'>🤖 MediBot</div>", unsafe_allow_html=True)

    # ---- Chat Scroll Container ----
    chat_html = "<div class='chat-container' id='chatbox'>"
    for q, a in st.session_state.chat_history:
        chat_html += f"<div class='user-msg'>👤 You: {q}</div>"
        chat_html += f"<div class='bot-msg'>🤖 MediBot: {a}</div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # ---- Auto-scroll script ----
    st.markdown("""
    <script>
        var chatBox = window.parent.document.querySelectorAll('section.main div[data-testid="stMarkdownContainer"] div.chat-container');
        if(chatBox.length > 0){
            chatBox[0].scrollTop = chatBox[0].scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

    # ---- Input Form ----
    with st.form("ask_form", clear_on_submit=True):
        user_input = st.text_input("Ask something medical...", key="user_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input.strip():
        response = get_disease_info(user_input)
        st.session_state.chat_history.append((user_input.strip(), response))

    st.markdown("<div class='footer'>Made with ❤️ | MediBot © 2025</div>", unsafe_allow_html=True)

# ---- App Flow ----
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_chat()
