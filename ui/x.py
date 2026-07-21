import gradio as gr
from app.pipeline import ingest, pipeline
import pandas as pd
import json
from datetime import datetime

# session store
_sessions = {}
_session_counter = [0]

def _new_id():
    _session_counter[0] += 1
    return f"session_{_session_counter[0]}"

def _sidebar_html(active_id=None):
    if not _sessions:
        return "<p style='color:#6b7280;font-size:13px;padding:8px 4px'>No sessions yet.</p>"
    groups = {"TODAY": [], "YESTERDAY": [], "EARLIER": []}
    now = datetime.now()
    for sid, data in reversed(list(_sessions.items())):
        ts = data.get("timestamp", now)
        delta = (now - ts).days
        if delta == 0:
            groups["TODAY"].append((sid, data))
        elif delta == 1:
            groups["YESTERDAY"].append((sid, data))
        else:
            groups["EARLIER"].append((sid, data))

    html = ""
    for group, items in groups.items():
        if not items:
            continue
        html += f"<p style='color:#6b7280;font-size:11px;font-weight:600;letter-spacing:.08em;margin:16px 0 6px;padding:0 4px'>{group}</p>"
        for sid, data in items:
            active_style = "background:#1e3a5f;border-left:3px solid #3b82f6;" if sid == active_id else "border-left:3px solid transparent;"
            name = data["name"][:22] + "..." if len(data["name"]) > 22 else data["name"]
            ts_str = data.get("ts_str", "just now")
            html += f"""
            <div style='
                {active_style}
                padding:10px 12px;
                border-radius:6px;
                margin-bottom:4px;
                display:flex;
                align-items:flex-start;
                gap:8px;
                color:#e2e8f0;
            '>
                <span style='font-size:15px;margin-top:1px'>📄</span>
                <div>
                    <div style='font-size:13px;font-weight:500;color:#e2e8f0'>{name}</div>
                    <div style='font-size:11px;color:#6b7280;margin-top:2px'>{ts_str}</div>
                </div>
            </div>"""
    count = len(_sessions)
    html += f"<div style='margin-top:24px;padding-top:12px;border-top:1px solid #2d3748'><span style='color:#6b7280;font-size:12px'>🗂 {count} session{'s' if count != 1 else ''} saved</span></div>"
    return html

def _sources_html(rows):
    if not rows:
        return """
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:300px;color:#4b5563'>
            <div style='font-size:36px;margin-bottom:12px'>🔍</div>
            <div style='font-size:14px'>Ask a question to see sources.</div>
        </div>"""
    html = ""
    for row in rows:
        page = row.get("Page", "N/A")
        preview = row.get("Preview", "")
        score = row.get("Score", None)
        try:
            score_float = float(score)
            score_pct = f"{int(score_float * 100)}%"
            bar_width = f"{int(score_float * 100)}%"
        except (TypeError, ValueError):
            score_pct = "N/A"
            bar_width = "0%"
        html += f"""
        <div style='
            background:#1a1d27;
            border:1px solid #2d3748;
            border-radius:10px;
            padding:14px;
            margin-bottom:12px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px'>
                <span style='
                    background:#1e3a5f;
                    color:#3b82f6;
                    font-size:12px;
                    font-weight:600;
                    padding:3px 10px;
                    border-radius:20px;
                '>Page {page}</span>
                <span style='color:#9ca3af;font-size:12px'>{score_pct} match</span>
            </div>
            <div style='height:3px;background:#2d3748;border-radius:2px;margin-bottom:10px'>
                <div style='height:100%;width:{bar_width};background:#3b82f6;border-radius:2px'></div>
            </div>
            <div style='color:#d1d5db;font-size:13px;line-height:1.6'>{preview}</div>
        </div>"""
    return html


# backend functions

def process_upload(file):
    if file is None:
        return None, [], _sidebar_html(), _sources_html([])
    try:
        session = ingest(file.name)
        doc_name = file.name.split("\\")[-1].split("/")[-1]
        sid = _new_id()
        now = datetime.now()
        _sessions[sid] = {
            "name": doc_name,
            "session_obj": session,
            "history": [],
            "timestamp": now,
            "ts_str": "just now"
        }
        return (
            sid,
            [{"role": "assistant", "content": f"✓ **{doc_name}** is ready. Ask me anything about it."}],
            _sidebar_html(active_id=sid),
            _sources_html([])
        )
    except Exception as e:
        return None, [{"role": "assistant", "content": f"❌ Failed to process document: {e}"}], _sidebar_html(), _sources_html([])


def handle_query(query, history, sid, fu1, fu2, fu3):
    if history is None:
        history = []

    if sid is None or sid not in _sessions:
        history = history + [{"role": "assistant", "content": "Please upload a document first."}]
        return history, _sources_html([]), gr.update(), gr.update(), gr.update()

    if not query.strip():
        return history, _sources_html([]), gr.update(), gr.update(), gr.update()

    session = _sessions[sid]["session_obj"]
    response, follow_ups = pipeline(session, query)

    history = history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response}
    ]
    _sessions[sid]["history"] = history

    from app.retrieval import retrieval_and_reranking
    top_k, _ = retrieval_and_reranking(session, query)
    metadata = top_k.get("metadatas", []) if top_k.get("metadatas") else []
    rows = []
    for i, meta in enumerate(metadata):
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
        rows.append({
            "Page": meta.get("page_number", "N/A") if isinstance(meta, dict) else "N/A",
            "Score": meta.get("score", "N/A") if isinstance(meta, dict) else "N/A",
            "Preview": top_k["documents"][i][:150] + "..." if top_k.get("documents") else ""
        })

    f1 = follow_ups[0] if len(follow_ups) > 0 else ""
    f2 = follow_ups[1] if len(follow_ups) > 1 else ""
    f3 = follow_ups[2] if len(follow_ups) > 2 else ""

    return (
        history,
        _sources_html(rows),
        gr.update(value=f1),
        gr.update(value=f2),
        gr.update(value=f3)
    )


def use_follow_up(question, history, sid):
    if not question:
        return history, _sources_html([]), gr.update(), gr.update(), gr.update()
    return handle_query(question, history, sid, "", "", "")


def clear_for_new_chat():
    return None, [], _sources_html([])


css = """
footer { display: none !important; }
.gradio-container { max-width: 100% !important; padding: 0 !important; }
body, .gradio-container { background: #0f1117 !important; }

#ragify-header {
    background: #0f1117;
    border-bottom: 1px solid #2d3748;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 10px;
}

#sidebar-col {
    background: #111318 !important;
    border-right: 1px solid #2d3748 !important;
    min-height: 92vh;
    padding: 16px !important;
}

/* new chat button — compact, not full width */
#new-chat-btn button {
    background: #3b82f6 !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    width: auto !important;
    height: 36px !important;
    margin-bottom: 8px !important;
}

#upload-col {
    padding: 16px !important;
}

#chatbot-area {
    background: #0f1117 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 12px !important;
}

/* user bubble */
.message-wrap .user > div {
    background: #3b82f6 !important;
    color: white !important;
    border-radius: 18px 18px 4px 18px !important;
}

/* assistant bubble */
.message-wrap .bot > div {
    background: #1a1d27 !important;
    color: #e2e8f0 !important;
    border-radius: 18px 18px 18px 4px !important;
    border: 1px solid #2d3748 !important;
}

#query-row textarea {
    background: #1a1d27 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 14px !important;
    resize: none !important;
}
#query-row textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
}

#submit-btn button {
    background: #3b82f6 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: white !important;
    height: 44px !important;
}

/* follow up buttons — unselected look, no highlight */
#fu-row button {
    background: transparent !important;
    border: 1px solid #374151 !important;
    color: #9ca3af !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 5px 12px !important;
    box-shadow: none !important;
    outline: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 220px !important;
}
#fu-row button:hover {
    background: #1e3a5f !important;
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}
#fu-row button:focus {
    box-shadow: none !important;
    outline: none !important;
}

#sources-panel {
    background: #111318 !important;
    border-left: 1px solid #2d3748 !important;
    padding: 16px !important;
    min-height: 92vh;
}
"""

theme = gr.themes.Base().set(
    body_background_fill="#0f1117",
    body_background_fill_dark="#0f1117",
    block_background_fill="#1a1d27",
    block_background_fill_dark="#1a1d27",
    block_border_color="#2d3748",
    body_text_color="#e2e8f0",
    button_primary_background_fill="#3b82f6",
    button_primary_background_fill_hover="#2563eb",
    button_primary_text_color="white",
    button_secondary_background_fill="transparent",
    button_secondary_background_fill_hover="#1e3a5f",
    button_secondary_border_color="#374151",
    button_secondary_text_color="#9ca3af",
    input_background_fill="#1a1d27",
    input_border_color="#2d3748",
    input_border_color_focus="#3b82f6",
    input_placeholder_color="#6b7280",
)


with gr.Blocks(title="RAGify") as demo:
    sid_state = gr.State(None)

    gr.HTML("""
    <div id="ragify-header">
        <span style="font-size:20px;color:#3b82f6">✦</span>
        <span style="font-size:20px;font-weight:700;color:#e2e8f0">RAGify</span>
        <span style="color:#6b7280;font-size:13px;margin-left:8px">Upload any document. Ask anything.</span>
    </div>
    """)

    with gr.Row(equal_height=True):

        # sidebar
        with gr.Column(scale=1, elem_id="sidebar-col", min_width=190):
            new_chat_btn = gr.Button("＋ New Chat", elem_id="new-chat-btn", variant="primary", size="sm")
            sidebar_html = gr.HTML(_sidebar_html())

        # main area
        with gr.Column(scale=4, elem_id="upload-col"):
            with gr.Row():
                upload = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                    scale=3
                )

            chatbot = gr.Chatbot(
                height=460,
                show_label=False,
                elem_id="chatbot-area",
                placeholder="<div style='text-align:center;color:#4b5563;margin-top:80px'><div style='font-size:36px'>📄</div><div style='margin-top:8px;font-size:14px'>Upload a document to get started</div></div>"
            )

            with gr.Row(elem_id="query-row"):
                query_input = gr.Textbox(
                    placeholder="Ask a question about your document...",
                    show_label=False,
                    lines=1,
                    scale=5
                )
                submit_btn = gr.Button("Send ↑", variant="primary", scale=1, elem_id="submit-btn")

            with gr.Row(elem_id="fu-row"):
                fu_btn_1 = gr.Button("", size="sm", variant="secondary")
                fu_btn_2 = gr.Button("", size="sm", variant="secondary")
                fu_btn_3 = gr.Button("", size="sm", variant="secondary")

        # sources panel
        with gr.Column(scale=2, elem_id="sources-panel", min_width=260):
            gr.HTML("<div style='font-size:14px;font-weight:600;color:#e2e8f0;padding-bottom:10px;border-bottom:1px solid #2d3748;margin-bottom:16px'>✦ Sources Used</div>")
            sources_html = gr.HTML(_sources_html([]))

    # wiring
    upload.change(
        fn=process_upload,
        inputs=[upload],
        outputs=[sid_state, chatbot, sidebar_html, sources_html]
    )

    submit_btn.click(
        fn=handle_query,
        inputs=[query_input, chatbot, sid_state, fu_btn_1, fu_btn_2, fu_btn_3],
        outputs=[chatbot, sources_html, fu_btn_1, fu_btn_2, fu_btn_3]
    ).then(fn=lambda: "", outputs=[query_input])

    query_input.submit(
        fn=handle_query,
        inputs=[query_input, chatbot, sid_state, fu_btn_1, fu_btn_2, fu_btn_3],
        outputs=[chatbot, sources_html, fu_btn_1, fu_btn_2, fu_btn_3]
    ).then(fn=lambda: "", outputs=[query_input])

    fu_btn_1.click(
        fn=use_follow_up,
        inputs=[fu_btn_1, chatbot, sid_state],
        outputs=[chatbot, sources_html, fu_btn_1, fu_btn_2, fu_btn_3]
    )
    fu_btn_2.click(
        fn=use_follow_up,
        inputs=[fu_btn_2, chatbot, sid_state],
        outputs=[chatbot, sources_html, fu_btn_1, fu_btn_2, fu_btn_3]
    )
    fu_btn_3.click(
        fn=use_follow_up,
        inputs=[fu_btn_3, chatbot, sid_state],
        outputs=[chatbot, sources_html, fu_btn_1, fu_btn_2, fu_btn_3]
    )

    new_chat_btn.click(
        fn=clear_for_new_chat,
        outputs=[sid_state, chatbot, sources_html]
    )

if __name__ == "__main__":
    demo.launch(
        theme=theme,
        css=css
    )
