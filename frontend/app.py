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
