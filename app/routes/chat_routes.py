from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import ChatRequest
from app.database import get_db
from app.models import ChatHistory, User
from app.security import current_user
from app.vector_store import search_chunks
from app.embedding_service import get_embedding
from app.rag_service import generate_answer
from app.llm_service import model_reply

router = APIRouter()


@router.post("/chat")
def chat_with_ai(
    data: ChatRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):

    question = data.message

    question_embedding = get_embedding(question)

    chunks = search_chunks(question_embedding)

    if chunks:

        context = "\n".join(chunks)

        answer = generate_answer(context, question)

        mode = "website"

    else:

        answer = model_reply(question)

        mode = "general"

    chat = ChatHistory(
        user_id=user.id,
        message=question,
        response=answer,
        mode=mode
    )

    db.add(chat)
    db.commit()
    


    return {
        "question": question,
        "answer": answer,
        "mode": mode
    }