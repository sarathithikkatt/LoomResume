import uuid

from sqlalchemy import (
    ARRAY,
    Column,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID as PG_UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import UserDefinedType

from app.core.config import settings

Base = declarative_base()

# Use configured embedding dimensions (768 for Ollama nomic-embed-text, 1536 for OpenAI)
EMBED_DIM = settings.EMBEDDING_DIMENSIONS


class VECTOR(UserDefinedType):
    def __init__(self, dimensions: int = EMBED_DIM):
        self.dimensions = dimensions

    def get_col_spec(self, **kw):
        return f"VECTOR({self.dimensions})"

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        return None


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    personal_info = Column(JSONB)
    summary = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ExperienceNode(Base):
    __tablename__ = "experience_nodes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    company = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    duration = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    raw_text = Column(Text, nullable=False)
    tags = Column(ARRAY(Text))
    embedding = Column(VECTOR(EMBED_DIM))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(Text, nullable=False)
    description = Column(Text)
    tags = Column(ARRAY(Text))
    embedding = Column(VECTOR(EMBED_DIM))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SkillsProfile(Base):
    __tablename__ = "skills_profile"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    skill_name = Column(Text, nullable=False)
    category = Column(Text)
    details = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Refraction(Base):
    __tablename__ = "refractions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(PG_UUID(as_uuid=True), nullable=False)
    source_type = Column(Text, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    lens = Column(Text, nullable=False)
    reframed_text = Column(Text, nullable=False)
    embedding = Column(VECTOR(EMBED_DIM))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("source_id", "lens", name="uq_refractions_source_id_lens"),)


class JDSession(Base):
    __tablename__ = "jd_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    jd_text = Column(Text, nullable=False)
    keywords = Column(ARRAY(Text))
    jd_embedding = Column(VECTOR(EMBED_DIM))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ResumeOutput(Base):
    __tablename__ = "resume_outputs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    experience_node_ids = Column(ARRAY(PG_UUID(as_uuid=True)))
    project_ids = Column(ARRAY(PG_UUID(as_uuid=True)))
    final_content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
