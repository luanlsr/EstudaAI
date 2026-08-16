import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    document_version = Column(String, nullable=False)
    knowledge_base_version = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    authority = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey('documents.id', ondelete='CASCADE'))
    document_version = Column(String, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text)
    ocr_used = Column(Boolean, default=False)

    document = relationship("Document", back_populates="pages")

class Chunk(Base):
    __tablename__ = 'chunks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, ForeignKey('documents.id', ondelete='CASCADE'))
    document_version = Column(String, nullable=False)
    knowledge_base_version = Column(String, nullable=False)
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    chapter = Column(String)
    section = Column(String)
    subsection = Column(String)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    content_hash = Column(String, nullable=False)
    
    # 1536 is standard for OpenAI text-embedding-3-small/text-embedding-ada-002
    embedding = Column(Vector(1536))

    document = relationship("Document", back_populates="chunks")
