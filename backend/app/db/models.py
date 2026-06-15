from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime
)

from datetime import datetime
from app.db.database import Base

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    state_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    project_id = Column(String)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True)
    project_id = Column(String)
    agent_name = Column(String)
    status = Column(String)
    output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Build(Base):
    __tablename__ = "builds"
    id = Column(String, primary_key=True)
    project_id = Column(String)
    success = Column(Boolean)
    build_logs = Column(Text)
    build_error = Column(Text)
    retry_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

