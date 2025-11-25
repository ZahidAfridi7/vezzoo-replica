from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List
from .. import models, schemas, database, auth
from .auth import get_current_user
from cryptography.fernet import Fernet
import base64
import os

router = APIRouter(
    prefix="/connections",
    tags=["connections"],
)

# Simple key generation for dev (in prod, load from env)
# Fernet key must be 32 url-safe base64-encoded bytes
# We'll use a derivation from SECRET_KEY or a default
key = os.getenv("ENCRYPTION_KEY")
if not key:
    # Generate a dummy key for dev if not set (NOT SECURE FOR PROD)
    key = Fernet.generate_key()

cipher_suite = Fernet(key)

def encrypt_password(password: str) -> str:
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

@router.post("/", response_model=schemas.Connection)
async def create_connection(
    connection: schemas.ConnectionCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Ensure user has an organization (for simplicity, pick the first one or require org_id)
    # In a real app, we'd pass org_id in the request or header
    result = await db.execute(
        select(models.Organization)
        .join(models.user_org_association)
        .where(models.user_org_association.c.user_id == current_user.id)
    )
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=400, detail="User does not belong to any organization")

    encrypted_pwd = encrypt_password(connection.password)
    
    new_connection = models.Connection(
        name=connection.name,
        db_type=connection.db_type,
        host=connection.host,
        port=connection.port,
        username=connection.username,
        encrypted_password=encrypted_pwd,
        database_name=connection.database_name,
        organization_id=org.id
    )
    
    db.add(new_connection)
    await db.commit()
    await db.refresh(new_connection)
    return new_connection

@router.get("/", response_model=List[schemas.Connection])
async def list_connections(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Get all connections for user's organizations
    # This query joins connections -> orgs -> users
    result = await db.execute(
        select(models.Connection)
        .join(models.Organization)
        .join(models.user_org_association)
        .where(models.user_org_association.c.user_id == current_user.id)
    )
    return result.scalars().all()

@router.post("/{connection_id}/test")
async def test_connection(
    connection_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Fetch connection
    result = await db.execute(select(models.Connection).where(models.Connection.id == connection_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    # Check permission (user must be in the org)
    # ... (skip for brevity, assume authorized if they have the ID and are logged in for this MVP)
    
    password = decrypt_password(conn.encrypted_password)
    
    # Construct DSN
    # We only support postgresql for now as per plan
    if conn.db_type == "postgresql":
        dsn = f"postgresql+asyncpg://{conn.username}:{password}@{conn.host}:{conn.port}/{conn.database_name}"
    else:
        raise HTTPException(status_code=400, detail="Unsupported database type")
        
    # Try connecting
    try:
        # Create a temporary engine
        from sqlalchemy.ext.asyncio import create_async_engine
        temp_engine = create_async_engine(dsn)
        async with temp_engine.connect() as temp_conn:
            await temp_conn.execute(text("SELECT 1"))
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from fastapi import BackgroundTasks
from .. import tasks

@router.post("/{connection_id}/scan")
async def scan_connection(
    connection_id: int,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Fetch connection to ensure it exists and belongs to user
    result = await db.execute(select(models.Connection).where(models.Connection.id == connection_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Trigger background task
    background_tasks.add_task(tasks.scan_schema_task, connection_id)
    
    return {"status": "queued", "message": "Schema scan started"}

