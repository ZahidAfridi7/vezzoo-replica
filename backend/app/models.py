from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for User <-> Organization (Many-to-Many)
user_org_association = Table(
    'user_org_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('organization_id', Integer, ForeignKey('organizations.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organizations = relationship("Organization", secondary=user_org_association, back_populates="users")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", secondary=user_org_association, back_populates="organizations")
    connections = relationship("Connection", back_populates="organization")

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    db_type = Column(String, nullable=False)  # postgresql, mysql, etc.
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    database_name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="connections")
    nodes = relationship("SchemaNode", back_populates="connection")
    edges = relationship("SchemaEdge", back_populates="connection")

class SchemaNode(Base):
    __tablename__ = "schema_nodes"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    name = Column(String, nullable=False)  # Table name
    type = Column(String, nullable=False)  # "table", "view"
    metadata_json = Column(String, nullable=True)  # JSON string of columns, types
    
    connection = relationship("Connection", back_populates="nodes")
    outgoing_edges = relationship("SchemaEdge", foreign_keys="[SchemaEdge.source_id]", back_populates="source")
    incoming_edges = relationship("SchemaEdge", foreign_keys="[SchemaEdge.target_id]", back_populates="target")

class SchemaEdge(Base):
    __tablename__ = "schema_edges"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("schema_nodes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("schema_nodes.id"), nullable=False)
    type = Column(String, nullable=False)  # "foreign_key"
    metadata_json = Column(String, nullable=True)  # JSON string of details (e.g. column mapping)

    connection = relationship("Connection", back_populates="edges")
    source = relationship("SchemaNode", foreign_keys=[source_id], back_populates="outgoing_edges")
    target = relationship("SchemaNode", foreign_keys=[target_id], back_populates="incoming_edges")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    connection = relationship("Connection")
    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user", "assistant"
    content = Column(String, nullable=False)
    sql_query = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")



