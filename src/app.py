import streamlit as st
import requests
import json
import os

# Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    h1 {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 242, 254, 0.3);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1f2937;
        border-radius: 8px;
        color: white;
    }
    
    /* Success/Info Messages */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'test_cases' not in st.session_state:
    st.session_state['test_cases'] = []
if 'context' not in st.session_state:
    st.session_state['context'] = []
if 'scripts' not in st.session_state:
    st.session_state['scripts'] = {} # Key: Test_ID, Value: Script
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'target_html' not in st.session_state:
    # Load default HTML if available
    if os.path.exists("checkout.html"):
        with open("checkout.html", "r") as f:
            st.session_state['target_html'] = f.read()
    else:
        st.session_state['target_html'] = "<!-- No checkout.html found -->"

# --- Sidebar: Configuration & Knowledge Base ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/robot-2.png", width=80)
    st.title("QA Agent Config")
    
    # Config
    with st.expander("⚙️ Settings", expanded=False):
        llm_model = st.text_input("LLM Model", value="gemini-flash-latest", help="e.g., gemini-flash-latest, gemini-pro")
        try:
            requests.get(BACKEND_URL, timeout=1)
            st.success("Backend: Online")
        except:
            st.error("Backend: Offline")

    st.markdown("---")
    
    # Knowledge Base Section
    st.header("📚 Knowledge Base")
    st.markdown("Upload project documents to train the agent.")
    
    uploaded_files = st.file_uploader(
        "Drop files here", 
        accept_multiple_files=True,
        type=['pdf', 'md', 'txt', 'json', 'html'],
        key="kb_uploader"
    )
    
    if st.button("🚀 Build Knowledge Base", use_container_width=True):
        if uploaded_files:
            with st.spinner("🧠 Ingesting documents..."):
                files = [('files', (f.name, f, f.type)) for f in uploaded_files]
                try:
                    response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                    if response.status_code == 200:
                        st.balloons()
                        st.success("Knowledge Base Built!")
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend.")
        else:
            st.warning("Upload files first.")

# --- Main Content ---
st.title("🤖 Autonomous QA Agent")
st.markdown("#### Your AI-powered partner for automated testing.")

# Tabs
tab1, tab2 = st.tabs(["🚀 QA Agent", "💬 Chat Assistant"])

# --- Tab 1: QA Agent (Unified) ---
with tab1:
    # 1. Target HTML (Collapsible)
    # 1. Target HTML (Collapsible)
    with st.expander("📄 Target HTML Context (Click to View/Edit)"):
        st.session_state['target_html'] = st.text_area(
            "HTML Source Code", 
            value=st.session_state['target_html'], 
            height=200
        )
        st.session_state['target_url'] = st.text_input(
            "Target URL (for Selenium)",
            value=st.session_state.get('target_url', "http://localhost:8000/checkout.html"),
            placeholder="e.g., http://localhost:8000/checkout.html or file:///absolute/path/to/file.html"
        )

    # 2. Test Generation Input
    st.subheader("1️⃣ Generate Test Cases")
    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_area(
            "Requirement Description", 
            value="Generate all positive and negative test cases for the discount code feature.",
            height=80,
            label_visibility="collapsed",
            placeholder="Describe what you want to test..."
        )
    with col2:
        generate_btn = st.button("✨ Generate Tests", use_container_width=True)
    
    # Handle Generation
    if generate_btn:
        with st.spinner("🕵️ Analyzing requirements..."):
            try:
                payload = {"query": user_query, "model": llm_model}
                response = requests.post(f"{BACKEND_URL}/generate-tests", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state['test_cases'] = data.get("result", [])
                    st.session_state['context'] = data.get("context", [])
                    if "warning" in data:
                        st.warning(data["warning"])
                    st.success(f"Generated {len(st.session_state['test_cases'])} test cases!")
                else:
                    st.error(f"Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend.")

    # 3. Test Cases List & Script Generation
    if st.session_state['test_cases']:
        st.markdown("---")
        st.subheader("2️⃣ Review Tests & Generate Scripts")
        
        # Global Download for Tests
        json_str = json.dumps(st.session_state['test_cases'], indent=2)
        st.download_button("📥 Download All Tests (JSON)", json_str, "test_cases.json", "application/json")
        
        for i, tc in enumerate(st.session_state['test_cases']):
            tc_id = tc.get('Test_ID', f'TC-{i+1}')
            tc_title = tc.get('Test_Scenario', 'Untitled')
            
            with st.expander(f"**{tc_id}: {tc_title}**"):
                # Test Details
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Feature:** {tc.get('Feature')}")
                    st.markdown(f"**Source:** `{tc.get('Grounded_In', 'Unknown')}`")
                with c2:
                    st.markdown("**Expected Result:**")
                    expected_result = tc.get('Expected_Result')
                    if isinstance(expected_result, (dict, list)):
                        st.json(expected_result)
                    else:
                        st.write(expected_result)
                
                # Generate Script Button
                if st.button(f"📜 Generate Script for {tc_id}", key=f"btn_{tc_id}"):
                    with st.spinner(f"Writing Selenium code for {tc_id}..."):
                        try:
                            payload = {
                                "test_case": json.dumps(tc),
                                "html_content": st.session_state['target_html'],
                                "target_url": st.session_state.get('target_url', ""),
                                "model": llm_model
                            }
                            response = requests.post(f"{BACKEND_URL}/generate-script", json=payload)
                            if response.status_code == 200:
                                script = response.json().get("script", "")
                                st.session_state['scripts'][tc_id] = script
                            else:
                                st.error(f"Error: {response.text}")
                        except Exception as e:
                            st.error(f"Failed: {str(e)}")

                # Display Script if available
                if tc_id in st.session_state['scripts']:
                    st.download_button(
                        f"📥 Download Script ({tc_id})",
                        st.session_state['scripts'][tc_id],
                        f"test_script_{tc_id}.py",
                        "text/x-python",
                        key=f"dl_{tc_id}"
                    )
                    st.markdown("##### 🐍 Generated Script")
                    st.code(st.session_state['scripts'][tc_id], language="python")

# --- Tab 2: Chat Assistant ---
with tab2:
    st.header("Chat with Documentation")
    
    for msg in st.session_state['chat_history']:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("Ask a question about your project...")
    
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {"query": user_input, "model": llm_model}
                    response = requests.post(f"{BACKEND_URL}/chat", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "")
                        st.write(answer)
                        st.session_state['chat_history'].append({"role": "assistant", "content": answer})
                        with st.expander("📚 Sources"):
                            st.write(data.get("context", []))
                    else:
                        st.error("Failed to get response.")
                except:
                    st.error("Backend connection failed.")
