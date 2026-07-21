import gradio as gr
from app.pipeline import ingest, pipeline
import pandas as pd
import json

def process_upload(file):
    if file is None:
        return None, "No file uploaded.", gr.update()
    try:
        session = ingest(file.name)
        doc_name = file.name.split("\\")[-1].split("/")[-1]
        # Return an empty list [] to clear the chatbot component
        return session, f"✓ {doc_name} processed and ready.", []
    except Exception as e:
        return None, f"Failed to process document: {e}", gr.update()


def handle_query(query, history, session, follow_up_1, follow_up_2, follow_up_3):
    # Initialize history if empty or malformed
    if history is None:
        history = []

    if session is None:
        history.append({"role": "assistant", "content": "Please upload a document first."})
        return history, pd.DataFrame(), gr.update(), gr.update(), gr.update()

    if not query.strip():
        return history, pd.DataFrame(), gr.update(), gr.update(), gr.update()

    # Process pipeline query
    response, follow_ups = pipeline(session, query)

    # Append using Gradio 6.x compliant message format
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": response})

    # Retrieval metadata
    from app.retrieval import retrieval_and_reranking
    top_k, _ = retrieval_and_reranking(session, query)
    metadata = top_k.get("metadatas", []) if top_k.get("metadatas") else []
    rows = []

    for i, meta in enumerate(metadata):
        # Safe JSON checking for stringified metadata values
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}

        rows.append({
            "Chunk": i + 1,
            "Page": meta.get("page_number", "N/A") if isinstance(meta, dict) else "N/A",
            "Preview": top_k["documents"][i][:120] + "..." if top_k.get("documents") else ""
        })

    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Chunk", "Page", "Score", "Preview"]
    )

    # Dynamically extract follow ups or fall back to empty strings
    f1 = follow_ups[0] if len(follow_ups) > 0 else ""
    f2 = follow_ups[1] if len(follow_ups) > 1 else ""
    f3 = follow_ups[2] if len(follow_ups) > 2 else ""

    # Return structured updates to correctly re-populate button component configurations
    return history, df, gr.update(value=f1), gr.update(value=f2), gr.update(value=f3)


def use_follow_up(question, history, session):
    if not question:
        return history, pd.DataFrame(), gr.update(), gr.update(), gr.update()
    return handle_query(question, history, session, "", "", "")


with gr.Blocks(title="DocuChat") as demo:
    session_state = gr.State(None)

    gr.Markdown(
        """
        # DocuChat
        Upload any PDF and have a grounded conversation with it.
        Every answer is sourced directly from your document.
        """
    )

    with gr.Row():
        upload = gr.File(
            label="Upload PDF",
            file_types=[".pdf"],
            scale=3
        )
        status = gr.Markdown("Upload a document to get started.")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_label=True
            )
            query_input = gr.Textbox(
                placeholder="Ask a question about your document...",
                label="Your question",
                lines=2
            )
            submit_btn = gr.Button("Ask", variant="primary")

            with gr.Row():
                fu_btn_1 = gr.Button("", size="sm", visible=True)
                fu_btn_2 = gr.Button("", size="sm", visible=True)
                fu_btn_3 = gr.Button("", size="sm", visible=True)

        with gr.Column(scale=2):
            gr.Markdown("### Retrieved Chunks")
            chunk_table = gr.Dataframe(
                headers=["Chunk", "Page", "Score", "Preview"],
                label="Sources used for this answer",
                wrap=True,
                max_height=500
            )

    # Wire upload pipeline
    upload.change(
         fn=process_upload,
         inputs=[upload],
         outputs=[session_state, status, chatbot]  # added chatbot here
     )

    # Wire submit interaction
    submit_btn.click(
        fn=handle_query,
        inputs=[query_input, chatbot, session_state, fu_btn_1, fu_btn_2, fu_btn_3],
        outputs=[chatbot, chunk_table, fu_btn_1, fu_btn_2, fu_btn_3]
    ).then(
        fn=lambda: "",
        outputs=[query_input]
    )

    # Wire keyboard enter submission
    query_input.submit(
        fn=handle_query,
        inputs=[query_input, chatbot, session_state, fu_btn_1, fu_btn_2, fu_btn_3],
        outputs=[chatbot, chunk_table, fu_btn_1, fu_btn_2, fu_btn_3]
    ).then(
        fn=lambda: "",
        outputs=[query_input]
    )

    # Wire follow up buttons click paths
    fu_btn_1.click(
        fn=use_follow_up,
        inputs=[fu_btn_1, chatbot, session_state],
        outputs=[chatbot, chunk_table, fu_btn_1, fu_btn_2, fu_btn_3]
    )
    fu_btn_2.click(
        fn=use_follow_up,
        inputs=[fu_btn_2, chatbot, session_state],
        outputs=[chatbot, chunk_table, fu_btn_1, fu_btn_2, fu_btn_3]
    )
    fu_btn_3.click(
        fn=use_follow_up,
        inputs=[fu_btn_3, chatbot, session_state],
        outputs=[chatbot, chunk_table, fu_btn_1, fu_btn_2, fu_btn_3]
    )


if __name__ == "__main__":
    demo.launch(share=True)
