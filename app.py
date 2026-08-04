
import gradio as gr
import html
from app.pipeline import ingest, pipeline, manager

CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ============ DESIGN TOKENS ============ */
    #app_body {

        --paper: #F1F4F7;
        --paper-deep: #E7ECF1;
        --ink: #17212B;
        --input-box-text:#bed5ed;
        --ink-soft: #4B5A6A;
        --line: #C6D1DB;
        --trace: #2255C4;
        --trace-deep: #163E94;
        --copper: #B8703A;
        --signal: #3F8F73;
        --radius-md: 8px;
        --radius-sm: 4px;

        --body-background-fill: var(--paper);
        --background-fill-primary: var(--paper);
        --background-fill-secondary: var(--paper-deep);
        --body-text-color: var(--ink);
        --body-text-color-subdued: var(--ink-soft);
        --border-color-primary: var(--line);
        --color-accent: var(--trace);
        --button-primary-background-fill: var(--trace);
        --button-primary-background-fill-hover: var(--trace-deep);
        --button-primary-text-color: #FFFFFF;
        --button-secondary-background-fill: var(--paper-deep);
        --button-secondary-border-color: var(--line);
        --input-background-fill: #FFFFFF;

        --input-text-color: var(--input-box-text);
        --input-text-weight: 500;
        --input-placeholder-color: var(--ink-soft);

        --block-border-color: var(--line);
        --block-radius: var(--radius-md);
        --font: 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;

        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-y: scroll !important;
        background: var(--paper) !important;
        color: var(--ink);
    }

    @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; transition-duration: 0.001ms !important; }
    }

    button:focus-visible, input:focus-visible, textarea:focus-visible, [tabindex]:focus-visible {
        outline: 2px solid var(--trace) !important;
        outline-offset: 2px !important;
    }

    /* ============ TEXT VISIBILITY & CONTRAST ============ */
    textarea, input[type="text"] {
        color: var(--input-box-text) !important;
        -webkit-text-fill-color: var(--input-box-text) !important;
        font-weight: 500 !important;
    }
    textarea::placeholder, input[type="text"]::placeholder {
        color: var(--ink-soft) !important;
        -webkit-text-fill-color: var(--ink-soft) !important;
        opacity: 0.7 !important;
    }

    .message-wrap .user {
        background-color: var(--trace) !important;
        border: 1px solid var(--trace-deep) !important;
        color: #FFFFFF !important;
    }
    .message-wrap .user * {
        color: #FFFFFF !important;
    }
    .message-wrap .bot {
        background-color: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        color: var(--ink) !important;
    }

    /* ============ HEADER ============ */
    #header {
        display: flex;
        flex: 1;
        flex-direction: column;
        justify-content: center;
        padding: 24px 0 16px 20px;
        border-bottom: 1px solid var(--line);
        background: var(--paper);
    }

    #header h1 {
        text-align: left;
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        font-family: "Space Grotesk", sans-serif;
        letter-spacing: -0.02em;
        line-height: 1.1;
        color: var(--ink);
    }

    #header h1::before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        background: var(--trace);
        border-radius: 50%;
        margin-right: 10px;
        vertical-align: middle;
    }

    #header p {
        text-align: left;
        margin: 6px 0 0 18px;
        font-size: 0.92rem;
        font-weight: 400;
        font-family: "Inter", sans-serif;
        color: var(--ink-soft);
        letter-spacing: -0.01em;
    }

    /* ============ MAIN LAYOUT ============ */
    #main {
        height: auto !important;
        flex: 8 !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 16px;
        padding: 16px 20px;
        box-sizing: border-box;
        overflow-y: auto !important;
        justify-content: center !important;
    }

    /* ============ LEFT SIDEBAR ============ */
    #left_sidebar {
        min-width: 220px;
        background: var(--paper-deep);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 16px 12px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    #left_sidebar h3 {
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--ink-soft);
        margin: 8px 4px 6px 4px;
    }

    #left_sidebar .prose,
    #left_sidebar .prose p {
        margin: 4px 4px 4px 4px !important;
        padding: 0 !important;
        font-family: "Inter", sans-serif;
        font-size: 0.85rem;
        color: var(--ink-soft);
        font-style: italic;
    }

    #new_chat_btn {
        background: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        font-family: "Inter", sans-serif !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        margin-bottom: 8px;
    }

    #new_chat_btn:hover {
        background: var(--paper-deep) !important;
        border-color: var(--trace) !important;
        color: var(--trace-deep) !important;
    }

    .session-btn {
        text-align: left;
        justify-content: flex-start;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
        font-family: "Inter", sans-serif !important;
        font-size: 0.88rem !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: var(--radius-sm) !important;
        color: var(--ink) !important;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    .session-btn:hover {
        background: #FFFFFF !important;
        border-color: var(--line) !important;
    }

    .session-btn.active {
        font-weight: 600;
        background: #FFFFFF !important;
        border-left: 3px solid var(--trace) !important;
        color: var(--trace-deep) !important;
    }

    /* ============ CENTER CHAT ============ */
    #chat {
        background:
            linear-gradient(var(--paper) 0%, var(--paper) 100%),
            repeating-linear-gradient(0deg, rgba(34,85,196,0.045) 0px, rgba(34,85,196,0.045) 1px, transparent 1px, transparent 28px),
            repeating-linear-gradient(90deg, rgba(34,85,196,0.045) 0px, rgba(34,85,196,0.045) 1px, transparent 1px, transparent 28px);
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 8.5 !important;
        height: 100% !important;
        overflow-y: scroll;
    }

    #chatbot {
        background: transparent !important;
        border: none !important;
        flex-grow: 1 !important;
        min-height: 0 !important;
    }

    #chat button {
        color: var(--ink-soft) !important;
        background: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        opacity: 1 !important;
    }

    #chat button:hover {
        color: var(--trace-deep) !important;
        border-color: var(--trace) !important;
    }

    /* ============ LOADING INDICATORS ============ */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.92em;
        font-family: "Inter", sans-serif;
        color: var(--copper);
    }

    .typing-indicator .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--copper);
        opacity: 0.4;
        animation: typing-bounce 1.2s infinite ease-in-out;
    }
    .typing-indicator .dot:nth-child(2) { animation-delay: 0.15s; }
    .typing-indicator .dot:nth-child(3) { animation-delay: 0.3s; }

    @keyframes typing-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-4px); opacity: 1; }
    }

    .upload-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.92em;
        font-family: "Inter", sans-serif;
        color: var(--trace);
    }
    .upload-indicator .spinner {
        width: 14px;
        height: 14px;
        border: 2px solid var(--trace);
        border-top-color: transparent;
        border-radius: 50%;
        opacity: 0.8;
        animation: spin 0.8s linear infinite;
        flex-shrink: 0;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ============ RIGHT SIDEBAR ============ */
    #right_sidebar {
        flex: 0 0 240px !important;
        min-width: 240px;
        background: var(--paper-deep);
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        padding: 16px 14px;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        display: block !important;
        box-sizing: border-box !important;
    }

    #right_sidebar div {
        display: block !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    #right_sidebar h3 {
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--ink-soft);
        margin: 0 0 12px 0;
        width: 100%;
        text-align: left;
        display: block !important;
    }

    .sources-column {
        display: block !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .source-chunk {
        position: relative;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 2px solid var(--trace);
        border-radius: var(--radius-sm);
        padding: 10px 12px 10px 14px;
        margin-bottom: 10px !important;
        font-size: 0.85em;
        animation: source-in 0.25s ease-out;
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }

    .source-chunk .source-meta {
        font-family: "JetBrains Mono", monospace;
        font-weight: 500;
        font-size: 0.78em;
        color: var(--trace-deep);
        margin-bottom: 5px;
        letter-spacing: 0.02em;
        display: block !important;
    }

    .source-chunk .source-text {
        font-family: "Inter", sans-serif;
        color: var(--ink-soft);
        white-space: pre-wrap;
        max-height: 120px;
        overflow-y: auto;
        line-height: 1.4;
        display: block !important;
    }

    /* ============ FOOTER ============ */
    #footer {
        flex: 0.4 !important;
        border-top: 1px solid var(--line) !important;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--paper);
        z-index: 100 !important;
        flex: 1 !important;
    }

    #footer h3 {
        text-align: center !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        font-family: "JetBrains Mono", monospace !important;
        color: var(--ink-soft) !important;
        letter-spacing: 0.04em;
        margin: 0 !important;
    }

    /* ============ RESPONSIVE LAYOUT (TABLET & MOBILE) ============ */
    @media (max-width: 992px) {
    #app_body {
        height: auto !important;
        min-height: 100dvh !important;
        display: block !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }

    #main {
        display: flex !important;
        flex-direction: column !important;
        height: auto !important;
        padding: 12px !important;
        gap: 12px !important;
        overflow: visible !important;
    }

    #left_sidebar {
        width: 100% !important;
        flex: none !important;
        height: auto !important;
        max-height: 200px !important;
        overflow-y: auto !important;
    }

    #chat {
        width: 100% !important;
        flex: none !important;
        height: auto !important;
        min-height: unset !important;
        max-height: unset !important;
        overflow: visible !important;
    }

    #chatbot {
        height: 400px !important;
        max-height: 400px !important;
        min-height: unset !important;
        overflow-y: scroll !important;
    }

    #right_sidebar {
        width: 100% !important;
        flex: none !important;
        height: auto !important;
        max-height: 300px !important;
        overflow-y: auto !important;
    }
}

@media (max-width: 480px) {
    #chatbot {
        height: 350px !important;
        max-height: 350px !important;
    }

    #header h1 { font-size: 1.6rem; }
    #header p { font-size: 0.85rem; }
    .source-chunk { font-size: 0.8rem; }
    .typing-indicator, .upload-indicator { font-size: 0.85em; }
}
"""

THINKING_HTML = """<span class="typing-indicator">Thinking<span class="dot"></span><span class="dot"></span><span class="dot"></span></span>"""
UPLOADING_HTML = """<span class="upload-indicator"><span class="spinner"></span>Processing document...</span>"""

def _history_from_session(session):
    return [{"role": t.role, "content": t.content} for t in session.chat_history]

def switch_session(sid, session_data_dict):
    session = manager.get_session(sid)
    if session is None:
        gr.Warning("This session is no longer available.")
        return [], None, None, gr.update(choices=[], visible=False), []

    # Check if we have saved follow-ups and sources for this specific session
    data = session_data_dict.get(sid, {})
    saved_follow_ups = data.get("follow_ups", [])
    saved_sources = data.get("sources", [])

    radio_update = gr.update(choices=saved_follow_ups, value=None, visible=bool(saved_follow_ups))

    return _history_from_session(session), session, sid, radio_update, saved_sources

def start_new_chat():
    return [], None, None, gr.update(value={"text": "", "files": []}), gr.update(choices=[], visible=False), []

def handle_submit(message, history, session, active_id, sessions_meta, session_data_dict):
    if isinstance(message, dict):
        files = message.get("files", [])
        text = message.get("text", "").strip()
    else:
        files = []
        text = str(message).strip()

    clear_input = gr.update(value={"text": "", "files": []})

    if files:
        history = history + [{"role": "user", "content": {"path": files[0]}}]
        history = history + [{"role": "assistant", "content": UPLOADING_HTML}]
        yield history, session, active_id, sessions_meta, clear_input, gr.update(visible=False), [], session_data_dict

        session = ingest(files[0])
        history[-1]["content"] = f"Loaded **{session.filename}** — ask away."
        active_id = session.session_id

        sessions_meta = dict(sessions_meta)
        sessions_meta[active_id] = session.filename

        yield history, session, active_id, sessions_meta, clear_input, gr.update(visible=False), [], session_data_dict
        return

    history = history + [{"role": "user", "content": text}]
    history = history + [{"role": "assistant", "content": THINKING_HTML}]
    yield history, session, active_id, sessions_meta, clear_input, gr.update(visible=False), [], session_data_dict

    if session is None:
        history[-1]["content"] = "Please upload a document first."
        yield history, session, active_id, sessions_meta, clear_input, gr.update(visible=False), [], session_data_dict
        return

    response, follow_ups, sources = pipeline(session, text)
    history[-1]["content"] = response

    # Update the session data dictionary so we remember these values if the user switches back
    session_data_dict = dict(session_data_dict)
    if active_id:
        session_data_dict[active_id] = {
            "follow_ups": follow_ups,
            "sources": sources
        }

    yield (
        history,
        session,
        active_id,
        sessions_meta,
        clear_input,
        gr.update(choices=follow_ups, value=None, visible=bool(follow_ups)),
        sources,
        session_data_dict
    )

def handle_follow_up_click(choice, history, session, active_id, sessions_meta, session_data_dict):
    yield from handle_submit({"text": choice, "files": []}, history, session, active_id, sessions_meta, session_data_dict)


with gr.Blocks(css=CSS, js="() => { document.body.classList.remove('dark'); }", title="RAGify", fill_width=True) as demo:
    session_state = gr.State(None)
    active_session_id = gr.State(None)
    sessions_meta = gr.State({})
    current_sources = gr.State([])

    # State mapping session IDs to their last follow_ups and sources
    session_data = gr.State({})

    with gr.Row(elem_id="app_body") as body:
        # Header
        with gr.Row(elem_id="header") as header:
            gr.HTML(
                "<h1>RAGify</h1>"
                "<p>Per-document Q&A, powered by retrieval.</p>"
            )

        # Main Layout
        with gr.Row(elem_id="main") as main:
            with gr.Column(elem_id="left_sidebar") as left:
                new_chat_btn = gr.Button("+ New chat", elem_id="new_chat_btn")
                gr.HTML("<h3>Sessions</h3><p style='opacity:0.6;font-size:0.8em;'>Resets on app restart</p>")

                @gr.render(inputs=[sessions_meta, active_session_id])
                def render_sessions(meta, active_id):
                    if not meta:
                        gr.Markdown("_No sessions yet_")
                        return
                    for sid, filename in meta.items():
                        btn = gr.Button(
                            filename,
                            elem_classes=["session-btn", "active"] if sid == active_id else ["session-btn"],
                        )
                        btn.click(
                            switch_session,
                            inputs=[gr.State(sid), session_data],
                            outputs=[chatbot, session_state, active_session_id, follow_up_radio, current_sources],
                        )

            with gr.Column(elem_id="chat") as middle:
                chatbot = gr.Chatbot(elem_id="chatbot", type="messages", height="500", show_label=False)
                follow_up_radio = gr.Radio(label="Follow-up questions", visible=False)

                chat_input = gr.MultimodalTextbox(
                    interactive=True,
                    file_count="multiple",
                    placeholder="Enter message or upload file...",
                    show_label=False,
                )

            with gr.Column(elem_id="right_sidebar") as right:
                gr.HTML("<h3>Sources</h3>")

                @gr.render(inputs=[current_sources])
                def render_sources_display(sources):
                    if not sources:
                        gr.Markdown("_No sources for this answer yet_")
                        return

                    with gr.Column(elem_classes="sources-column"):
                        for i, src in enumerate(sources):
                            if isinstance(src, dict):
                                metadata = src.get("metadata", {})
                                page_num = metadata.get("page_number")
                                meta_display = f"Page {page_num}" if page_num is not None else f"Source {i+1}"
                                text = src.get("text", "")
                            else:
                                meta_display = f"Source {i+1}"
                                text = str(src)

                            html_content = f"""
                            <div class="source-chunk">
                                <div class="source-meta">{html.escape(meta_display)}</div>
                                <div class="source-text">{html.escape(text)}</div>
                            </div>
                            """
                            gr.HTML(html_content)

        # Triggers
        new_chat_btn.click(
            start_new_chat,
            outputs=[chatbot, session_state, active_session_id, chat_input, follow_up_radio, current_sources],
        )

        chat_input.submit(
            handle_submit,
            inputs=[chat_input, chatbot, session_state, active_session_id, sessions_meta, session_data],
            outputs=[chatbot, session_state, active_session_id, sessions_meta, chat_input, follow_up_radio, current_sources, session_data],
        )

        follow_up_radio.select(
            handle_follow_up_click,
            inputs=[follow_up_radio, chatbot, session_state, active_session_id, sessions_meta, session_data],
            outputs=[chatbot, session_state, active_session_id, sessions_meta, chat_input, follow_up_radio, current_sources, session_data],
        )

        with gr.Row(elem_id="footer") as footer:
            gr.HTML(
                "<h3>Made with ❤️ in 🇬🇭</h3>"
            )

demo.launch()
