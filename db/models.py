from sqlalchemy import (
    Column, Integer, String, Text, Date, Boolean, Float, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    fake = Column(Boolean, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    about = Column(Text, nullable=True)
    pts = Column(Integer, nullable=True)
    participants_count = Column(Integer, nullable=False, default=0)
    pinned_msg_id = Column(Integer, nullable=True)
    linked_chat_id = Column(Integer, nullable=True)

    # Add index for faster search on frequently queried columns
    __table_args__ = (
        Index("ix_channels_username", "username"),
    )


class PostText(Base):
    __tablename__ = "post_texts"

    id = Column(Integer, primary_key=True)
    peer_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    date = Column(Date, nullable=False)
    message = Column(Text, nullable=True)
    views = Column(Integer, nullable=False, default=0)
    forwards = Column(Integer, nullable=False, default=0)
    edit_date = Column(Date, nullable=True)
    #embedding = Column(Vector(384), nullable=True)

    # Establish relationship with Channel for easier ORM navigation
    channel = relationship("Channel", back_populates="posts")

    __table_args__ = (
        Index("ix_post_texts_date", "date"),
    )


Channel.posts = relationship("PostText", order_by=PostText.date, back_populates="channel")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    summary = Column(Text, nullable=False)
    date = Column(Date, nullable=False)


class SummarySource(Base):
    __tablename__ = "summary_sources"

    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post_texts.id"), nullable=False)
    peer_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    source = Column(Text, nullable=False)

    # Relationships to facilitate joins and ensure data integrity
    summary = relationship("Summary", back_populates="sources")
    post = relationship("PostText")
    channel = relationship("Channel")

    __table_args__ = (
        Index("ix_summary_sources_summary_id", "summary_id"),
        Index("ix_summary_sources_post_id", "post_id"),
    )


Summary.sources = relationship("SummarySource", order_by=SummarySource.id, back_populates="summary")


class PostEntity(Base):
    __tablename__ = "post_entities"

    id = Column(Integer, primary_key=True)
    peer_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    entities = Column(Text, nullable=True)

    channel = relationship("Channel")

    __table_args__ = (
        Index("ix_post_entities_peer_id", "peer_id"),
    )


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from dotenv import load_dotenv
    import os

    load_dotenv()

    connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
