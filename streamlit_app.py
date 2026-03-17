import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State ──────────────────────────────────────────────────────────────
defaults = {
    "token": None,
    "user_name": None,
    "chat_history": [],
    "websites_added": 0,
    "total_chunks": 0,
    "last_mode": "—",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 RAG Assistant")
    st.divider()

    if st.session_state.token:
        st.success(f"👤 **{st.session_state.user_name}**")
        col1, col2 = st.columns(2)
        col1.metric("Sites", st.session_state.websites_added)
        col2.metric("Chunks", st.session_state.total_chunks)
        st.divider()

    menu = st.radio(
        "Navigate",
        ["🏠 Home", "🔑 Signup", "🔒 Login", "🌐 Add Website", "💬 Ask AI"],
        label_visibility="collapsed"
    )

    if st.session_state.token:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["token", "user_name", "chat_history", "websites_added", "total_chunks", "last_mode"]:
                st.session_state[k] = defaults[k]
            st.rerun()

    st.divider()
    st.caption("Powered by Google Gemini + RAG")

# ── HOME ──────────────────────────────────────────────────────────────────────
if menu == "🏠 Home":
    st.title("🤖 RAG AI Assistant")
    st.subheader("Chat with any website using AI")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🔑 Step 1 — Sign Up**\n\nCreate a free account to get started.")
    with col2:
        st.info("**🌐 Step 2 — Add a Website**\n\nPaste any URL. The AI will read and index it.")
    with col3:
        st.info("**💬 Step 3 — Ask AI**\n\nAsk anything. Get smart answers from the content.")

    st.divider()

    if not st.session_state.token:
        st.warning("👋 You are not logged in. Use the sidebar to **Sign Up** or **Login**.")
    else:
        st.success(f"Welcome back, **{st.session_state.user_name}**! Head to **Add Website** or **Ask AI** to continue.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Websites Added", st.session_state.websites_added)
        c2.metric("Chunks Indexed", st.session_state.total_chunks)
        c3.metric("Messages Sent", len(st.session_state.chat_history))

# ── SIGNUP ────────────────────────────────────────────────────────────────────
elif menu == "🔑 Signup":
    col_form, col_info = st.columns([2, 1], gap="large")

    with col_form:
        st.title("Create Account")
        st.caption("Get started — it's completely free.")
        st.divider()

        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="john@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 8 characters")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")
            submitted = st.form_submit_button("✅ Create Account", use_container_width=True)

        if submitted:
            if not all([name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating your account..."):
                    try:
                        res = requests.post(
                            f"{BASE_URL}/signup",
                            json={"name": name, "email": email, "password": password}
                        )
                        if res.status_code == 200:
                            st.success("🎉 Account created! Switch to **Login** to sign in.")
                            st.balloons()
                        else:
                            st.error(res.json().get("detail", res.text))
                    except Exception as e:
                        st.error(f"Could not connect to server: {e}")

    with col_info:
        st.title(" ")
        st.divider()
        st.subheader("Why RAG Assistant?")
        st.write("✅ Ask questions from any website")
        st.write("✅ Powered by Google Gemini AI")
        st.write("✅ Persistent knowledge base")
        st.write("✅ Instant, accurate answers")

# ── LOGIN ─────────────────────────────────────────────────────────────────────
elif menu == "🔒 Login":
    col_form, col_spacer = st.columns([2, 1], gap="large")

    with col_form:
        st.title("Welcome Back")
        st.caption("Sign in to continue.")
        st.divider()

        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="john@example.com")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Keep me signed in")
            submitted = st.form_submit_button("🔒 Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                with st.spinner("Verifying credentials..."):
                    try:
                        res = requests.post(
                            f"{BASE_URL}/login",
                            json={"email": email, "password": password}
                        )
                        if res.status_code == 200:
                            st.session_state.token = res.json()["access_token"]
                            st.session_state.user_name = email.split("@")[0].capitalize()
                            st.session_state.chat_history = []
                            st.success("✅ Signed in! Navigate to **Ask AI** to start chatting.")
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password.")
                    except Exception as e:
                        st.error(f"Could not connect to server: {e}")

    with col_spacer:
        st.title(" ")
        st.divider()
        st.info("💡 **New here?** Switch to **Signup** in the sidebar to create a free account.")

# ── ADD WEBSITE ───────────────────────────────────────────────────────────────
elif menu == "🌐 Add Website":
    st.title("Add Website Knowledge")
    st.caption("Paste a URL — the AI will scrape, understand, and index its content.")
    st.divider()

    if not st.session_state.token:
        st.warning("⚠️ Please log in first.")
        st.stop()

    col_form, col_tips = st.columns([2, 1], gap="large")

    with col_form:
        with st.form("website_form"):
            url = st.text_input(
                "Website URL",
                placeholder="https://example.com/docs",
                help="Enter the full URL including https://"
            )
            submitted = st.form_submit_button("🚀 Process Website", use_container_width=True)

        if submitted:
            if not url:
                st.error("Please enter a URL.")
            elif not url.startswith("http"):
                st.error("URL must start with http:// or https://")
            else:
                progress = st.progress(0, text="Starting...")
                with st.spinner("Scraping and indexing..."):
                    try:
                        progress.progress(30, text="Fetching website content...")
                        res = requests.post(
                            f"{BASE_URL}/add-website",
                            json={"url": url},
                            headers={"Authorization": f"Bearer {st.session_state.token}"}
                        )
                        progress.progress(80, text="Storing embeddings...")
                        if res.status_code == 200:
                            result = res.json()
                            chunks = result.get("total_chunks", 0)
                            progress.progress(100, text="Done!")
                            st.session_state.websites_added += 1
                            st.session_state.total_chunks += chunks
                            st.success("✅ Website indexed successfully!")
                            st.metric("Chunks stored", chunks)
                        else:
                            progress.empty()
                            st.error(res.json().get("detail", res.text))
                    except Exception as e:
                        progress.empty()
                        st.error(f"Could not connect to server: {e}")

    with col_tips:
        st.subheader("📌 Tips")
        st.write("- Use **documentation** or **blog** URLs for best results")
        st.write("- Works with any publicly accessible page")
        st.write("- Chunk size depends on page length")
        st.divider()
        st.metric("Sites added this session", st.session_state.websites_added)
        st.metric("Total chunks indexed", st.session_state.total_chunks)

# ── ASK AI ────────────────────────────────────────────────────────────────────
elif menu == "💬 Ask AI":
    st.title("💬 Ask AI")

    if not st.session_state.token:
        st.warning("⚠️ Please log in first.")
        st.stop()

    # Top row stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Messages", len(st.session_state.chat_history))
    c2.metric("Websites Indexed", st.session_state.websites_added)
    c3.metric("Total Chunks", st.session_state.total_chunks)
    c4.metric("Last Mode", st.session_state.last_mode)

    st.divider()

    if not st.session_state.chat_history:
        st.info("👋 No messages yet. Ask your first question below!")

    # Chat history
    for turn in st.session_state.chat_history:
        with st.chat_message("user", avatar="🧑"):
            st.write(turn["question"])
            st.caption(turn.get("time", ""))
        with st.chat_message("assistant", avatar="🤖"):
            st.write(turn["answer"])
            st.caption(f"🔧 Mode: `{turn['mode']}`")

    # Chat input
    question = st.chat_input("Ask anything about the websites you've added...")

    if question:
        now = datetime.now().strftime("%I:%M %p")
        with st.chat_message("user", avatar="🧑"):
            st.write(question)
            st.caption(now)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(
                        f"{BASE_URL}/chat",
                        json={"message": question},
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    if res.status_code == 200:
                        result = res.json()
                        mode = result.get("mode", "RAG")
                        st.write(result["answer"])
                        st.caption(f"🔧 Mode: `{mode}`")
                        st.session_state.chat_history.append({
                            "question": result["question"],
                            "answer": result["answer"],
                            "mode": mode,
                            "time": now
                        })
                        st.session_state.last_mode = mode
                    else:
                        st.error(res.json().get("detail", res.text))
                except Exception as e:
                    st.error(f"Could not connect to server: {e}")

    # Actions row
    if st.session_state.chat_history:
        st.divider()
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.last_mode = "—"
                st.rerun()

        with col2:
            st.caption(f"💬 {len(st.session_state.chat_history)} message(s) in this session")