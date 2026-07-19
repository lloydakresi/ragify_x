from collections import deque
from .session import Session, ChatTurn
from .client import llm

def build_history_string(session: Session) -> str:
    turns = list(session.chat_history)

    if not turns:
        return ""

    parts = []

    # handle summary at position 0
    if turns[0].role == "summary":
        parts.append(f"SUMMARY OF EARLIER CONVERSATION:\n{turns[0].content}")
        turns = turns[1:]

    # format remaining turns
    recent = "\n".join(
        f"{turn.role.capitalize()}: {turn.content}"
        for turn in turns
    )

    if recent:
        parts.append(f"RECENT EXCHANGES:\n{recent}")

    return "\n\n".join(parts)

def history_management(session: Session):
    conversations = session.chat_history.copy()
    has_summary = conversations[0].role == "summary"

    if has_summary:
        summary = conversations[0].content

        old_user = conversations[1].content
        old_assistant = conversations[2].content
        exchanges_text = f"PREVIOUS SUMMARY:\n{summary}\n\nOLDER EXCHANGE:\nUser: {old_user}\nAssistant: {old_assistant}"
        del session.chat_history[2]
        del session.chat_history[1]
    else:
        old_user = conversations[0].content
        old_assistant = conversations[1].content
        exchanges_text = f"OLDER EXCHANGE:\nUser: {old_user}\nAssistant: {old_assistant}"
        del session.chat_history[1]
        del session.chat_history[0]


    SUMMARIZATION_PROMPT = f"""You are summarizing a conversation between a user and a document assistant.

    Below are older exchanges from the conversation. Summarize them into a single concise paragraph that captures the key topics discussed, questions asked, and answers given.
    Focus only on information that would be useful context for understanding future questions in the same conversation.
    Do not include greetings or filler. Be brief.

    EXCHANGES TO SUMMARIZE:
    {exchanges_text}\n

    Write only the summary paragraph, nothing else."""

    new_summary = llm(user_prompt=SUMMARIZATION_PROMPT)
    if has_summary:
        session.chat_history[0] = ChatTurn("summary", new_summary)
    else:
        session.chat_history.appendleft(ChatTurn("summary", new_summary))
