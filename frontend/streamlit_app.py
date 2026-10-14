import html
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
PAGES = ["Dashboard", "Documents", "Ask AI"]

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    :root {
        --bg: #080D1D;
        --sidebar: #0D1428;
        --panel: #151D32;
        --border: #293550;
        --text: #F2F5FC;
        --muted: #98A6C0;
        --blue: #22B8E6;
        --purple: #9665F5;
    }

    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stHeader"] { background: var(--bg); }
    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid #202A43;
    }
    [data-testid="stSidebar"] * { color: var(--text); }
    .block-container { max-width: 1500px; padding: 2rem 2.1rem 3rem; }
    h1, h2, h3, p, label { color: var(--text); }
    h1 { font-size: 2rem !important; font-weight: 750 !important; letter-spacing: -0.7px; }
    h2 { font-size: 1.3rem !important; }
    .muted { color: var(--muted); font-size: 0.9rem; }
    .brand { font-size: 1.35rem; font-weight: 800; letter-spacing: -0.5px; padding: 0.4rem 0 0.2rem; }
    .brand-icon { color: var(--blue); }
    .nav-label { color: var(--muted); font-size: 0.73rem; font-weight: 700; letter-spacing: 1.5px; margin: 1.8rem 0 0.6rem; }
    .stat-card {
        background: linear-gradient(135deg, #18233B, #121A2D);
        border: 1px solid var(--border); border-radius: 15px;
        padding: 1.1rem 1.2rem; min-height: 108px;
    }
    .stat-label { color: var(--muted); font-size: 0.84rem; }
    .stat-value { color: var(--text); font-size: 1.8rem; font-weight: 750; margin-top: 0.25rem; }
    .doc-card {
        background: linear-gradient(145deg, #18233A, #121A2D);
        border: 1px solid var(--border); border-radius: 15px;
        padding: 1.1rem; min-height: 150px; margin-bottom: 0.3rem;
    }
    .doc-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 39px; height: 39px; border-radius: 11px;
        background: #203D69; color: #73B6FF; font-size: 1.1rem; margin-bottom: 1rem;
    }
    .doc-name { font-weight: 700; font-size: 0.98rem; overflow-wrap: anywhere; margin-bottom: 0.35rem; }
    .doc-meta { color: var(--muted); font-size: 0.8rem; }
    .section-heading { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.25rem; }
    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 9px; min-height: 42px; font-weight: 600; border-color: var(--border);
    }
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #19BCE5, #8661F6) !important;
        border: none !important; color: #FFFFFF !important; border-radius: 9px; font-weight: 600;
    }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover { filter: brightness(1.12); }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        background: #11192B !important; color: var(--text) !important;
        border: 1px solid var(--border) !important; border-radius: 9px !important;
    }
    [data-testid="stFileUploader"] { background: #11192B; border: 1px dashed #354361; border-radius: 12px; padding: 0.7rem; }
    [data-testid="stFileUploader"] * { color: var(--text); }
    [data-testid="stAlert"] { border-radius: 10px; }
    hr { border-color: var(--border); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- API helpers ----------
def get_documents():
    response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
    response.raise_for_status()
    return response.json().get("documents", [])


# ---------- Session-state callbacks ----------
# Streamlit executes callbacks before rerunning the script and creating widgets.
# This makes it safe to update the state backing the navigation radio.
def open_document_in_ask_ai(document_id):
    st.session_state["selected_document_id"] = document_id
    st.session_state["active_page"] = "Ask AI"


def open_upload():
    st.session_state["show_upload"] = True
    st.session_state["active_page"] = "Documents"


def clear_document_scope():
    st.session_state.pop("selected_document_id", None)


# ---------- Initialise state before creating widgets ----------
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Dashboard"
if "show_upload" not in st.session_state:
    st.session_state["show_upload"] = False
if "selected_document_id" not in st.session_state:
    st.session_state["selected_document_id"] = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-icon">✦</span> DocuMind AI</div>'
        '<div class="muted">Your intelligent workspace</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-label">WORKSPACE</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        PAGES,
        key="active_page",
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-label">SYSTEM</div>', unsafe_allow_html=True)
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health.ok:
            st.success("● API connected")
        else:
            st.warning(f"API status: {health.status_code}")
    except requests.RequestException:
        st.error("API unavailable")

    st.divider()
    st.caption("PDF · TXT · DOCX")
    st.caption("Private document workspace")


# ---------- Load real data ----------
try:
    documents = get_documents()
    api_error = None
except requests.RequestException as exc:
    documents = []
    api_error = str(exc)

if api_error:
    st.error(f"Unable to load documents from the API: {api_error}")


# ---------- Shared page header ----------
def render_header(kicker, title, description, show_new_document=False):
    left, right = st.columns([3, 1])
    with left:
        st.markdown(
            f'<div class="muted">{html.escape(kicker)}</div>',
            unsafe_allow_html=True,
        )
        st.title(title)
        st.markdown(
            f'<div class="muted">{html.escape(description)}</div>',
            unsafe_allow_html=True,
        )
    if show_new_document:
        with right:
            st.write("")
            st.button(
                "＋  New document",
                type="primary",
                use_container_width=True,
                on_click=open_upload,
            )


def render_upload_area():
    expanded = st.session_state.get("show_upload", False)
    if expanded or page == "Documents":
        with st.expander("＋ Upload a document", expanded=expanded):
            uploaded_file = st.file_uploader(
                "Choose PDF, TXT or DOCX",
                type=["pdf", "txt", "docx"],
                key="dashboard_upload",
            )
            if st.button(
                "Upload to knowledge base",
                type="primary",
                key="upload_document_button",
            ):
                if uploaded_file is None:
                    st.warning("Choose a file first.")
                else:
                    try:
                        with st.spinner("Processing document..."):
                            response = requests.post(
                                f"{API_BASE_URL}/documents/upload",
                                files={
                                    "file": (
                                        uploaded_file.name,
                                        uploaded_file.getvalue(),
                                        uploaded_file.type or "application/octet-stream",
                                    )
                                },
                                timeout=300,
                            )
                            response.raise_for_status()

                        st.success("Document uploaded successfully.")
                        st.session_state["show_upload"] = False
                        st.rerun()
                    except requests.RequestException as exc:
                        st.error(f"Upload failed: {exc}")
                        if exc.response is not None:
                            st.caption(exc.response.text[:500])


def render_document_grid():
    st.markdown(
        '<div class="section-heading">Your documents</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="muted">Browse and search files in your knowledge base.</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search documents",
        placeholder="Search by filename...",
        label_visibility="collapsed",
        key="document_search",
    )
    filtered_documents = [
        doc
        for doc in documents
        if search.strip().lower() in doc.get("filename", "").lower()
    ]

    if not filtered_documents:
        st.info("No matching documents. Upload a document to get started.")
        return

    for start in range(0, len(filtered_documents), 3):
        columns = st.columns(3, gap="large")
        for column, doc in zip(columns, filtered_documents[start : start + 3]):
            filename = doc.get("filename", "Untitled document")
            safe_filename = html.escape(filename)
            extension = os.path.splitext(filename)[1].upper().lstrip(".") or "FILE"
            document_id = doc.get("document_id", "")

            with column:
                st.markdown(
                    f'<div class="doc-card">'
                    f'<div class="doc-icon">▤</div>'
                    f'<div class="doc-name">{safe_filename}</div>'
                    f'<div class="doc-meta">{html.escape(extension)} · Stored in knowledge base</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                with st.popover("Manage document"):
                    st.caption(f"Document ID: {document_id or 'Unavailable'}")

                    st.button(
                        "Ask about this document",
                        key=f"ask_{document_id}",
                        type="primary",
                        use_container_width=True,
                        on_click=open_document_in_ask_ai,
                        args=(document_id,),
                        disabled=not document_id,
                    )

                    st.divider()

                    confirm_delete = st.checkbox(
                        "I want to delete this document",
                        key=f"confirm_delete_{document_id}",
                    )

                    if st.button(
                        "Delete document",
                        key=f"delete_{document_id}",
                        disabled=not confirm_delete or not document_id,
                        use_container_width=True,
                    ):
                        try:
                            response = requests.delete(
                                f"{API_BASE_URL}/documents/{document_id}",
                                timeout=30,
                            )
                            response.raise_for_status()

                            if st.session_state.get("selected_document_id") == document_id:
                                st.session_state.pop("selected_document_id", None)

                            st.session_state.pop(f"confirm_delete_{document_id}", None)
                            st.success("Document deleted successfully.")
                            st.rerun()
                        except requests.RequestException as exc:
                            st.error(f"Could not delete the document: {exc}")
                            if exc.response is not None:
                                st.caption(exc.response.text[:500])


# ---------- Dashboard / Documents pages ----------
if page in ("Dashboard", "Documents"):
    kicker = (
        "WORKSPACE / OVERVIEW"
        if page == "Dashboard"
        else "WORKSPACE / DOCUMENTS"
    )
    title = "Workspace Docs" if page == "Dashboard" else "Document library"
    description = (
        "AI-powered document management"
        if page == "Dashboard"
        else "Search and manage your uploaded files."
    )
    render_header(kicker, title, description, show_new_document=True)

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-label">📄 Total documents</div>'
            f'<div class="stat-value">{len(documents)}</div></div>',
            unsafe_allow_html=True,
        )
    with stat2:
        st.markdown(
            '<div class="stat-card"><div class="stat-label">✦ AI assistant</div>'
            '<div class="stat-value">Ready</div></div>',
            unsafe_allow_html=True,
        )
    with stat3:
        st.markdown(
            '<div class="stat-card"><div class="stat-label">⌁ Supported formats</div>'
            '<div class="stat-value">3</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    render_upload_area()
    render_document_grid()


# ---------- Ask AI page ----------
if page == "Ask AI":
    render_header(
        "WORKSPACE / AI ASSISTANT",
        "Ask AI",
        "Ask questions and explore answers grounded in your documents.",
    )

    selected_id = st.session_state.get("selected_document_id")
    selected_document = next(
        (doc for doc in documents if doc.get("document_id") == selected_id),
        None,
    )
    if selected_id and selected_document is None:
        st.session_state.pop("selected_document_id", None)
        selected_id = None

    if selected_document:
        st.info(
            f"Question scope: **{selected_document.get('filename', 'Selected document')}**"
        )
        st.button(
            "Ask across all documents",
            key="clear_document_scope",
            on_click=clear_document_scope,
        )
    else:
        st.caption("Searching across all uploaded documents.")

    with st.form("ask_form"):
        question = st.text_area(
            "Your question",
            placeholder="e.g. What is the project mascot called?",
            height=120,
        )
        submitted = st.form_submit_button("Generate answer", type="primary")

    if submitted:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            params = {"question": question.strip(), "top_k": 5}
            if selected_id:
                params["document_id"] = selected_id

            try:
                with st.spinner("Searching documents and generating an answer..."):
                    response = requests.post(
                        f"{API_BASE_URL}/ask",
                        params=params,
                        timeout=180,
                    )
                    response.raise_for_status()
                    result = response.json()

                st.markdown("### Answer")
                st.markdown(result.get("answer", "No answer returned."))
                citations = result.get("citations", [])
                if citations:
                    st.markdown("### Sources")
                    for citation in citations:
                        st.info(
                            f"{citation.get('filename', 'Document')} · "
                            f"Page {citation.get('page', '?')}"
                        )
                else:
                    st.caption("No citations returned.")
            except requests.RequestException as exc:
                st.error(f"Question failed: {exc}")
                if exc.response is not None:
                    st.caption(exc.response.text[:500])
