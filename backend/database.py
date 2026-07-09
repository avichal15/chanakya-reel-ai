from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
import os

# Database Definition
class Philosopher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    bio: Optional[str] = None
    quotes: List["Quote"] = Relationship(back_populates="philosopher")

class Quote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    translation: Optional[str] = None
    meaning: Optional[str] = None
    language: str = "hi"  # Default Hindi/Sanskrit
    category: Optional[str] = None
    tags: Optional[str] = None # Comma separated
    is_used: bool = Field(default=False)
    philosopher_id: Optional[int] = Field(default=None, foreign_key="philosopher.id")
    philosopher: Optional[Philosopher] = Relationship(back_populates="quotes")

class GeneratedScript(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quote_id: int = Field(foreign_key="quote.id")
    full_text: str
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    status: str = "draft" # draft, scripting, voice_generated, rendering, completed

class VideoExport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_path: str
    video_url: str
    caption_text: str
    status: str = "completed"
    created_at: str = Field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

# Engine Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_FILE_NAME = os.path.join(BASE_DIR, "database.db")
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
