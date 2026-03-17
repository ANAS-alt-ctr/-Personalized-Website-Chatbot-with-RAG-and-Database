from fastapi import APIRouter,  Depends
from app.models import User,Website
from sqlalchemy.orm import Session
from app.scraper import scrape_website
from app.embedding_service import get_embedding
from app.vector_store import add_chunks
from app.rag_service import split_text
from pydantic import BaseModel
from app.security import current_user
from app.database import get_db
from app.schemas import WebsiteRequest



router = APIRouter()




@router.post("/add-website")
def add_website(data: WebsiteRequest,
                user: User = Depends(current_user),
                db: Session = Depends(get_db)
):

    text = scrape_website(data.url)

    chunks = split_text(text)

    embeddings = [get_embedding(chunk) for chunk in chunks]

    add_chunks(chunks, embeddings)

    web = Website(
            user_id=user.id,
            url=data.url,
            status="Done",
        )

    db.add(web)
    db.commit()



    return {
        "message": "Website processed successfully",
        "total_chunks": len(chunks)
    }