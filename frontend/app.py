import requests
import streamlit as st

SESSION = requests.Session()
SESSION.trust_env = False

API_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.session_state.token = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.set_page_config(
    page_title="RAG Chat with PDF",
    page_icon="📄",
    layout="wide",
)


st.title("📄 RAG Chat with PDF")
st.caption(
    "AI-powered document analysis, semantic search and intelligent answers."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = True

with st.sidebar:

    page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "📊 Dashboard",
            "📚 Documents",
            "📈 Analytics",
            "⚙️ Settings"
        ]
    )

    st.divider()

    st.header("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):
        try:
            response = SESSION.post(
                f"{API_URL}/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
                timeout=30,
            )

            if response.ok:
                data = response.json()
                st.session_state.token = data.get(
                    "access_token"
                )
                st.session_state.user_email = email
                st.success("Login successful")
            else:
                st.error(response.text)

        except requests.RequestException as exc:
            st.error(f"Login failed: {exc}")

    if st.session_state.token:
        st.success(
            "✅ Authenticated"
        )

        st.markdown(
            f"""
            ### 👤 Profile
            
            **User:**  
            {st.session_state.user_email}
            
            **Role:**  
            Document Analyst
            
            **AI Access:**  
            Enabled
            """
        )

        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

    st.divider()

    st.header("📄 Documents")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
    )

    if uploaded_file and st.button(
        "Index PDF",
        use_container_width=True,
    ):
        try:
            response = SESSION.post(
                f"{API_URL}/documents/upload",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                },
                headers={
                    "Authorization": f"Bearer {st.session_state.token}"
                },
                timeout=300,
            )

            if response.ok:
                result = response.json()

                st.success(
                    f"Indexed: {result.get('filename')}"
                )

                st.json(result)
            else:
                st.error(response.text)

        except requests.RequestException as exc:
            st.error(f"Backend connection failed: {exc}")

    st.divider()

    try:
        response = SESSION.get(
            f"{API_URL}/health",
            timeout=5,
        )

        if response.ok:
            health = response.json()

            if health.get("openai_configured"):
                st.success("Backend online")
            else:
                st.warning(
                    "Backend online — OpenAI key not configured."
                )
        else:
            st.error("Backend unavailable.")

    except requests.RequestException:
        st.warning("Start FastAPI first.")


if page == "📊 Dashboard":

    st.title("📊 RAG Dashboard")

    st.caption(
        "AI document intelligence overview"
    )

    import os

    pdf_count = len(
        [
            f for f in os.listdir("data/uploads")
            if f.endswith(".pdf")
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "PDF Documents",
            pdf_count
        )

    with col2:
        st.metric(
            "Vector DB",
            "ChromaDB"
        )

    with col3:
        st.metric(
            "Embedding",
            "ONNX"
        )

    with col4:
        st.metric(
            "LLM",
            "Ollama"
        )

    st.divider()

    st.success(
        "RAG Pipeline Ready"
    )

    st.info(
        "Upload PDF → Extract → Chunk → Embed → Retrieve → Generate"
    )

    st.divider()

    st.subheader(
        "🤖 AI Capabilities"
    )

    capabilities = [
        "✅ PDF Understanding",
        "✅ Semantic Search",
        "✅ Question Answering",
        "✅ Source Verification",
        "✅ Local AI Processing",
    ]

    for item in capabilities:
        st.write(item)

    st.divider()

    st.subheader(
        "💼 Business Value"
    )

    st.write(
        """
⏱ Reduce document review time

🔍 Search thousands of pages instantly

📄 Extract important information automatically

🔒 Keep documents private with local AI
"""
    )

    st.divider()

    st.subheader(
        "🧠 Smart Document Intelligence"
    )

    intelligence = [
        "🧾 Automatic document type detection",
        "📌 Key information extraction",
        "📝 AI generated summaries",
        "🔍 Semantic document search",
        "📚 Multi-document question answering",
    ]

    for item in intelligence:
        st.write(item)


    st.divider()

    st.subheader(
        "🏢 Enterprise Ready"
    )

    enterprise = [
        "🔐 Secure JWT authentication",
        "🗂 Document workspace management",
        "⚡ Fast AI retrieval",
        "🔒 Private local AI processing",
        "📄 Source verified answers",
    ]

    for item in enterprise:
        st.write(item)


    st.divider()


    st.divider()

    st.subheader(
        "🚀 AI Document Intelligence Platform"
    )

    st.write(
        """
Transform documents into instant knowledge.

✓ Reduce manual document review
✓ Find information in seconds
✓ Automate repetitive work
✓ Keep sensitive data private
"""
    )


    st.subheader(
        "📈 Supported Business Use Cases"
    )

    use_cases = [
        "Finance: Invoice analysis",
        "Legal: Contract search",
        "HR: Resume screening",
        "Operations: Document automation",
        "Customer Support: Knowledge assistant",
    ]

    for item in use_cases:
        st.write(item)





elif page == "📚 Documents":

    st.title("📚 Document Workspace")

    st.caption(
        "Manage and analyze your AI-ready documents"
    )

    import os

    search = st.text_input(
        "🔍 Search documents"
    )

    files = os.listdir("data/uploads")

    filtered = [
        f for f in files
        if search.lower() in f.lower()
    ]

    st.metric(
        "Total Documents",
        len(filtered)
    )

    st.divider()


    if filtered:

        for f in filtered:

            path = os.path.join(
                "data/uploads",
                f
            )

            size = round(
                os.path.getsize(path) / 1024,
                1
            )


            with st.container():

                st.subheader(
                    f"📄 {f}"
                )

                c1,c2,c3 = st.columns(3)

                c1.write(
                    "Type:\nPDF Document"
                )

                c2.write(
                    f"Size:\n{size} KB"
                )

                c3.write(
                    "Status:\nAI Ready ✅"
                )


                st.write(
                    """
Capabilities:

💬 Ask AI questions
📝 Generate summaries
🔍 Semantic search
📄 Source verification
"""
                )

                st.divider()

    else:
        st.warning(
            "No documents found."
        )



elif page == "📈 Analytics":

    st.title("📈 Analytics")

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Questions",
        len(st.session_state.messages)
    )

    c2.metric(
        "AI Engine",
        "Ollama"
    )

    c3.metric(
        "Status",
        "Online"
    )


elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.write(
        "AI Model: llama3.2:3b"
    )

    st.write(
        "Embedding: all-MiniLM-L6-v2 ONNX"
    )

    st.write(
        "Database: ChromaDB"
    )

    st.write(
        "Security: JWT Authentication"
    )

    st.write(
        "Processing: Local AI Pipeline"
    )

    st.write(
        "Architecture: FastAPI + Streamlit"
    )

    st.divider()

    st.subheader(
        "🔐 Security"
    )

    st.write(
        "JWT Authentication Enabled ✅"
    )

    st.write(
        "Private Document Processing ✅"
    )

    st.write(
        "Role Based Access Ready ✅"
    )



st.divider()

st.subheader("💬 Chat Intelligence")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Questions",
        len(
            [
                m for m in st.session_state.messages
                if m.get("role") == "user"
            ]
        )
    )

with col2:
    if st.button(
        "🧹 Clear Conversation"
    ):
        st.session_state.messages = []
        st.rerun()

for index, message in enumerate(
    st.session_state.messages,
    start=1
):
    with st.chat_message(message["role"]):

        if message["role"] == "user":
            st.caption(
                f"Question #{(index + 1)//2}"
            )

        st.markdown(message["content"])

        sources = message.get("sources", [])

        if sources:
            with st.expander("📄 Sources"):
                for source in sources:
                    filename = (
                        source.get("filename")
                        or "Unknown document"
                    )

                    page = source.get("page") or "?"

                    st.markdown(
                        f"**{filename}** — page {page}"
                    )

                    if source.get("score") is not None:
                        st.caption(
                            f"Distance: "
                            f"{source['score']:.4f}"
                        )

                    if source.get("text"):
                        st.caption(source["text"])

st.divider()

st.caption(
    f"💬 Conversation messages: {len(st.session_state.messages)}"
)


st.divider()

st.subheader(
    "🤖 AI Assistant Tools"
)

st.caption(
    "Ask intelligent questions about your documents"
)


suggestions = [
    "این سند درباره چیست",
    "اطلاعات اصلی این سند را استخراج کن.",
    "نام محصول قیمت و مشتری را پیدا کن.",
    "این سند را خلاصه کن.",
]


cols = st.columns(2)

for i, item in enumerate(suggestions):

    if cols[i % 2].button(
        "💡 " + item,
        use_container_width=True
    ):
        st.session_state.messages.append(
            {
                "role": "user",
                "content": item
            }
        )



st.subheader(
    "📊 Document Analysis"
)

a,b,c = st.columns(3)

a.info(
    "📝 Summary\nAI generated summary"
)

b.info(
    "🔍 Extraction\nKey information"
)

c.info(
    "📄 Report\nExport ready"
)



question = st.chat_input(
    "Ask a question about your documents..."
)

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            try:
                response = SESSION.post(
                    f"{API_URL}/chat",
                    json={"question": question},
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}"
                    },
                    timeout=300,
                )

                if response.ok:
                    result = response.json()

                    answer = result.get(
                        "answer",
                        "No answer returned.",
                    )

                    sources = result.get("sources", [])

                    st.success("🤖 AI Answer")

                    st.markdown(answer)

                    st.caption(
                        "Confidence: High | Based on retrieved PDF context"
                    )

                    if sources:
                        with st.expander("📄 Sources"):
                            for source in sources:
                                filename = (
                                    source.get("filename")
                                    or "Unknown"
                                )

                                page = (
                                    source.get("page")
                                    or "?"
                                )

                                st.markdown(
                                    f"**{filename}** — page {page}"
                                )

                                if source.get("text"):
                                    st.caption(
                                        source["text"]
                                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                else:
                    st.error(response.text)

            except requests.RequestException as exc:
                st.error(
                    f"Backend connection failed: {exc}"
                )
