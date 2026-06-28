import streamlit as st
import httpx
import os
import json
import uuid
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="PrepPilot Study Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Inject Custom CSS for Premium Look
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global Font & Theme Adjustments */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #0b0f19;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Gradient Title */
.gradient-title {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.gradient-subtitle {
    font-size: 1.2rem;
    color: #9ca3af;
    text-align: center;
    margin-bottom: 2rem;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
}

/* Subject Card Selection Hover UI */
.subject-card {
    background: rgba(30, 41, 59, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.subject-card:hover {
    transform: translateY(-5px);
    border-color: #60a5fa;
    box-shadow: 0 10px 20px -10px rgba(96, 165, 250, 0.3);
}

/* Metric Widgets */
.metric-box {
    background: rgba(17, 24, 39, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #60a5fa;
}

.metric-label {
    font-size: 0.85rem;
    color: #9ca3af;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.badge-connected {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.badge-disconnected {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

</style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "backend_url" not in st.session_state:
    st.session_state.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
if "page" not in st.session_state:
    st.session_state.page = "select_subject"
if "selected_subject_id" not in st.session_state:
    st.session_state.selected_subject_id = None
if "selected_subject_name" not in st.session_state:
    st.session_state.selected_subject_name = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = 0
if "tokens_available" not in st.session_state:
    st.session_state.tokens_available = 20000
if "api_error" not in st.session_state:
    st.session_state.api_error = None

# Local Session Persistence Helpers
def get_session_file_path(subject_id: int) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, f".session_{subject_id}.json")

def load_session_data(subject_id: int) -> dict | None:
    try:
        path = get_session_file_path(subject_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

def save_session_data(subject_id: int, session_id: str | None, chat_history: list, tokens_used: int, tokens_available: int):
    try:
        path = get_session_file_path(subject_id)
        data = {
            "session_id": session_id,
            "chat_history": chat_history,
            "tokens_used": tokens_used,
            "tokens_available": tokens_available
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def clear_session_data(subject_id: int):
    try:
        path = get_session_file_path(subject_id)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# Backend Connection Checker
def check_backend_health():
    try:
        response = httpx.get(f"{st.session_state.backend_url}/", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False

# Fetch all subjects
def get_subjects():
    try:
        response = httpx.get(f"{st.session_state.backend_url}/subjects", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("data", [])
        return []
    except Exception as e:
        st.error(f"Error connecting to server to fetch subjects: {e}")
        return []

# Create new subject (helper fallback)
def create_subject(subject_name: str):
    try:
        response = httpx.post(
            f"{st.session_state.backend_url}/subjects",
            json={"subject_name": subject_name},
            timeout=5.0
        )
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                return data["data"]
        return None
    except Exception as e:
        st.error(f"Error creating subject: {e}")
        return None

# SSE Chat Query Stream Generator
def ask_query_stream(query: str, subject_id: int, session_id: str | None):
    payload = {
        "query": query,
        "subject_id": subject_id,
        "session_id": session_id,
        "top_k": 5
    }
    
    try:
        with httpx.stream(
            "POST",
            f"{st.session_state.backend_url}/chats/query",
            json=payload,
            timeout=120.0
        ) as r:
            if r.status_code != 200:
                error_detail = "Unknown backend error"
                try:
                    error_json = r.read()
                    error_detail = json.loads(error_json).get("detail", error_detail)
                except Exception:
                    pass
                st.session_state.api_error = {
                    "status_code": r.status_code,
                    "detail": error_detail
                }
                return
            
            for line in r.iter_lines():
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if not data_str:
                        continue
                    try:
                        data_json = json.loads(data_str)
                        if isinstance(data_json, dict):
                            if data_json.get("done") is True:
                                # Update global states on complete response
                                st.session_state.session_id = data_json.get("session_id")
                                st.session_state.tokens_used = data_json.get("tokens_used", 0)
                                st.session_state.tokens_available = data_json.get("tokens_available", 20000)
                            elif "text" in data_json:
                                yield data_json["text"]
                        else:
                            yield str(data_json)
                    except json.JSONDecodeError:
                        # Raw text chunk
                        yield data_str
    except Exception as e:
        st.session_state.api_error = {
            "status_code": 500,
            "detail": f"Failed to establish communication with the backend service. ({e})"
        }
        return


# ========================================================
# PAGE: SELECT SUBJECT
# ========================================================
def page_select_subject():
    st.markdown('<div class="gradient-title">PrepPilot AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-subtitle">Your intelligent, interactive study companion</div>', unsafe_allow_html=True)
    
    # Connection Check Card in Sidebar
    backend_ok = check_backend_health()
    with st.sidebar:
        st.subheader("System Status")
        if backend_ok:
            st.markdown(f'<span class="badge badge-connected">● Connected to Backend ({st.session_state.backend_url})</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge badge-disconnected">● Backend Offline ({st.session_state.backend_url})</span>', unsafe_allow_html=True)
            st.warning("Ensure the PrepPilot FastAPI server is running.")
            
            # Allow configuring url
            custom_url = st.text_input("Backend Endpoint URL", st.session_state.backend_url)
            if custom_url != st.session_state.backend_url:
                st.session_state.backend_url = custom_url
                st.rerun()

    subjects = get_subjects() if backend_ok else []
    
    if subjects:
        st.write("Click on a subject card to start or resume your study room:")
        
        # Grid of subject cards
        cols = st.columns(3)
        for idx, sub in enumerate(subjects):
            col = cols[idx % 3]
            with col:
                local_sess = load_session_data(sub["subject_id"])
                has_session = local_sess is not None
                
                # Fetch details
                codes = sub.get("subject_codes") or []
                universities = sub.get("universities") or []
                slugs = sub.get("slugs") or []
                semester = sub.get("semester")
                
                code_str = f" | {', '.join(codes)}" if codes else ""
                semester_str = f"Semester {semester}" if semester else "Study Room"
                
                univ_badges = ""
                if universities:
                    univ_badges = "<div style='margin-top: 0.5rem;'>" + "".join(
                        f"<span style='background: rgba(96, 165, 250, 0.1); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.15); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.35rem; display: inline-block;'>🏫 {univ}</span>"
                        for univ in universities
                    ) + "</div>"
                    
                slug_badges = ""
                if slugs:
                    slug_badges = "<div style='margin-top: 0.25rem;'>" + "".join(
                        f"<span style='background: rgba(167, 139, 250, 0.1); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.15); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.35rem; display: inline-block;'>🔗 {slug}</span>"
                        for slug in slugs
                    ) + "</div>"
                
                st.markdown(
                    f"""
                    <div class="subject-card">
                        <h3 style="margin-bottom: 0.25rem; color: #f3f4f6; font-size: 1.35rem;">📚 {sub['subject_name']}</h3>
                        <p style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.25rem;">
                            <strong>{semester_str}</strong>{code_str}
                        </p>
                        {univ_badges}
                        {slug_badges}
                        <p style="color: #60a5fa; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">
                            {'🔄 Resumable Session' if has_session else '✨ New Study Session'}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)
                if st.button("Enter Chat Room", key=f"sub_btn_{sub['subject_id']}", use_container_width=True):
                    st.session_state.selected_subject_id = sub["subject_id"]
                    st.session_state.selected_subject_name = sub["subject_name"]
                    if has_session:
                        st.session_state.session_id = local_sess.get("session_id")
                        st.session_state.chat_history = local_sess.get("chat_history", [])
                        st.session_state.tokens_used = local_sess.get("tokens_used", 0)
                        st.session_state.tokens_available = local_sess.get("tokens_available", 20000)
                    else:
                        st.session_state.session_id = None
                        st.session_state.chat_history = []
                        st.session_state.tokens_used = 0
                        st.session_state.tokens_available = 20000
                    st.session_state.page = "chat"
                    st.rerun()
    else:
        if backend_ok:
            st.info("No subjects are registered in the system yet.")
        else:
            st.error("Unable to list subjects because the backend API is unreachable.")


# ========================================================
# DIALOGS
# ========================================================
@st.dialog("⚠️ System Alert: Limit Reached")
def show_limit_dialog(status_code: int, message: str):
    st.markdown(f"### Connection/Usage Limit Details")
    st.error(f"**Error Code:** {status_code}\n\n**Details:** {message}")
    st.write("You have hit the daily usage limit or the server is busy. Please try again later or reset the conversation.")
    if st.button("Close", use_container_width=True):
        st.rerun()


# ========================================================
# PAGE: CHAT ROOM
# ========================================================
def page_chat():
    subject_id = st.session_state.selected_subject_id
    subject_name = st.session_state.selected_subject_name
    
    # Sidebar: Session Metrics & Actions
    with st.sidebar:
        st.markdown(f"### 📖 {subject_name}")
        st.caption(f"Subject ID: {subject_id}")
        st.markdown("---")
        
        st.markdown("##### 🪙 Daily API Usage")
        # Token metrics
        used = st.session_state.tokens_used
        avail = st.session_state.tokens_available
        total = used + avail
        if total == 0:
            total = 20000
        
        # Calculate ratio
        ratio = float(used) / float(total) if total > 0 else 0.0
        ratio = min(max(ratio, 0.0), 1.0)
        
        st.progress(ratio)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{used}</div><div class="metric-label">Tokens Used</div></div>',
                unsafe_allow_html=True
            )
        with col_m2:
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{avail}</div><div class="metric-label">Remaining</div></div>',
                unsafe_allow_html=True
            )
            
        st.markdown("---")
        
        # Session ID management
        st.markdown("##### 🔑 Active Session ID")
        sess_id = st.session_state.session_id if st.session_state.session_id else "Not started (Will generate on query)"
        st.code(sess_id, language="text")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Navigation/Reset Action buttons
        if st.button("🔄 Reset Conversation", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.chat_history = []
            st.session_state.tokens_used = 0
            st.session_state.tokens_available = 20000
            clear_session_data(subject_id)
            st.success("Conversation reset!")
            st.rerun()
            
        if st.button("⬅️ Change Subject", use_container_width=True):
            st.session_state.page = "select_subject"
            st.rerun()

    # Chat Header
    st.markdown(f"### 💬 PrepPilot Study Room: **{subject_name}**")
    st.markdown(f"Ask any question about `{subject_name}` to retrieve information and converse with the LLM.")
    
    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat input
    if prompt := st.chat_input(f"Ask a question about {subject_name}..."):
        # Reset api_error
        st.session_state.api_error = None
        
        # Check token limit pre-flight
        if st.session_state.tokens_available <= 0:
            st.session_state.api_error = {
                "status_code": 429,
                "detail": "You have exhausted your available daily token quota. Please reset your conversation or try again tomorrow."
            }
            show_limit_dialog(429, st.session_state.api_error["detail"])
            st.rerun()
            
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display assistant response placeholder & stream
        with st.chat_message("assistant"):
            # Set up the stream
            response_placeholder = st.empty()
            full_response = ""
            
            # Show a spinner while initiating the stream and waiting for the first chunk
            with st.spinner("PrepPilot is thinking..."):
                stream_gen = ask_query_stream(prompt, subject_id, st.session_state.session_id)
                try:
                    first_chunk = next(stream_gen)
                except StopIteration:
                    first_chunk = ""
            
            # Now stream the rest of the response
            full_response += first_chunk
            if full_response:
                response_placeholder.markdown(full_response + "▌")
            
            # Read from generator chunk by chunk
            for chunk in stream_gen:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
            # Remove cursor and update final markdown
            response_placeholder.markdown(full_response)
            
        # Check if error occurred during request
        if st.session_state.api_error:
            # We got an error! Remove the failed user message from chat history
            st.session_state.chat_history.pop()
            show_limit_dialog(st.session_state.api_error["status_code"], st.session_state.api_error["detail"])
        else:
            # Add assistant response to history
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            # Save updated session data locally
            save_session_data(
                subject_id,
                st.session_state.session_id,
                st.session_state.chat_history,
                st.session_state.tokens_used,
                st.session_state.tokens_available
            )
            st.rerun()  # Rerun to update sidebar metrics (tokens used, session_id)


# ========================================================
# MAIN ROUTER
# ========================================================
def main():
    if st.session_state.page == "select_subject":
        page_select_subject()
    elif st.session_state.page == "chat":
        page_chat()

if __name__ == "__main__":
    main()
