from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, database
from .introspection.postgres import PostgresStrategy
from .routers.connections import decrypt_password
import json
import logging

logger = logging.getLogger(__name__)

async def scan_schema_task(connection_id: int):
    # Create a new session for the background task
    async with database.AsyncSessionLocal() as db:
        try:
            # Fetch connection
            result = await db.execute(select(models.Connection).where(models.Connection.id == connection_id))
            conn = result.scalars().first()
            if not conn:
                logger.error(f"Connection {connection_id} not found")
                return

            # Decrypt password
            password = decrypt_password(conn.encrypted_password)
            
            # Prepare params
            params = {
                "host": conn.host,
                "port": conn.port,
                "username": conn.username,
                "password": password,
                "database_name": conn.database_name
            }
            
            # Select strategy
            if conn.db_type == "postgresql":
                strategy = PostgresStrategy()
            else:
                logger.error(f"Unsupported db_type {conn.db_type}")
                return
            
            # Introspect
            logger.info(f"Starting scan for connection {connection_id}")
            graph_data = await strategy.introspect(params)
            
            # Save to DB
            # First, clear existing nodes/edges for this connection (simple replacement strategy)
            # In a real app, we might want to diff/merge
            await db.execute(models.SchemaEdge.__table__.delete().where(models.SchemaEdge.connection_id == connection_id))
            await db.execute(models.SchemaNode.__table__.delete().where(models.SchemaNode.connection_id == connection_id))
            
            # Create Nodes
            node_map = {} # name -> id
            for node_data in graph_data["nodes"]:
                node = models.SchemaNode(
                    connection_id=connection_id,
                    name=node_data["name"],
                    type=node_data["type"],
                    metadata_json=node_data["metadata"]
                )
                db.add(node)
                await db.flush() # to get ID
                node_map[node.name] = node.id
            
            # Create Edges
            for edge_data in graph_data["edges"]:
                source_id = node_map.get(edge_data["source"])
                target_id = node_map.get(edge_data["target"])
                
                if source_id and target_id:
                    edge = models.SchemaEdge(
                        connection_id=connection_id,
                        source_id=source_id,
                        target_id=target_id,
                        type=edge_data["type"],
                        metadata_json=edge_data["metadata"]
                    )
                    db.add(edge)
            
            await db.commit()
            logger.info(f"Scan completed for connection {connection_id}")
            
        except Exception as e:
            logger.error(f"Scan failed for connection {connection_id}: {e}")
            await db.rollback()
