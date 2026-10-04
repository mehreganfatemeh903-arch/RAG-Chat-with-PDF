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
    "Upload PDF documents and ask questions using "
    "retrieval-augmented generation."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:

    page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "📊 Dashboard",
            "📚 Documents",
            "📈 Analytics",
            "⚙️ Settings",
            "💬 Chat",
            "📊 Dashboard"
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
        st.info(
            f"Logged in: {st.session_state.user_email}"
        )

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
        "Upload PDF → Extract → Embed → Retrieve → Answer"
    )




if page == "📊 Dashboard":

    st.title("📊 RAG Dashboard")

    import os

    pdfs = [
        x for x in os.listdir("data/uploads")
        if x.endswith(".pdf")
    ]

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Documents",len(pdfs))
    c2.metric("Vector DB","ChromaDB")
    c3.metric("Embedding","ONNX")
    c4.metric("LLM","Ollama")

    st.divider()

    st.success("RAG Pipeline Healthy")

    st.write(
        "Upload → Extract → Chunk → Embed → Retrieve → Generate"
    )


elif page == "📚 Documents":

    st.title("📚 Document Library")

    import os

    files = os.listdir("data/uploads")

    if files:
        for f in files:

            path = os.path.join(
                "data/uploads",
                f
            )

            size = round(
                os.path.getsize(path)/1024,
                1
            )

            st.info(
                f"📄 {f}\n\n"
                f"Size: {size} KB\n\n"
                "Status: Indexed ✅"
            )
    else:
        st.warning(
            "No documents uploaded."
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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
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

                    st.markdown(answer)

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
