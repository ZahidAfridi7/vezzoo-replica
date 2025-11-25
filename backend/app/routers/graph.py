from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
)

@router.get("/{connection_id}", response_model=schemas.GraphData)
async def get_graph(
    connection_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Fetch connection
    result = await db.execute(select(models.Connection).where(models.Connection.id == connection_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    # Fetch nodes and edges
    # Use selectinload to fetch related data if needed, but here we query directly
    nodes_result = await db.execute(select(models.SchemaNode).where(models.SchemaNode.connection_id == connection_id))
    nodes = nodes_result.scalars().all()
    
    edges_result = await db.execute(select(models.SchemaEdge).where(models.SchemaEdge.connection_id == connection_id))
    edges = edges_result.scalars().all()
    
    return {"nodes": nodes, "edges": edges}
