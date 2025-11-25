from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ConnectionBase(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    username: str
    database_name: str

class ConnectionCreate(ConnectionBase):
    password: str

class Connection(ConnectionBase):
    id: int
    organization_id: int
    
    class Config:
        from_attributes = True

class SchemaNodeBase(BaseModel):
    name: str
    type: str
    metadata_json: Optional[str] = None

class SchemaNode(SchemaNodeBase):
    id: int
    connection_id: int
    
    class Config:
        from_attributes = True

class SchemaEdgeBase(BaseModel):
    source_id: int
    target_id: int
    type: str
    metadata_json: Optional[str] = None

class SchemaEdge(SchemaEdgeBase):
    id: int
    connection_id: int
    
    class Config:
        from_attributes = True

class GraphData(BaseModel):
    nodes: List[SchemaNode]
    edges: List[SchemaEdge]

class ChatMessageBase(BaseModel):
    role: str
    content: str
    sql_query: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    connection_id: int
    created_at: datetime
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    connection_id: int


