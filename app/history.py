from collections import deque
from .session import Session
conversations = deque(maxlen=3)

def history_management(session: Session):
    conversations.append(session)
