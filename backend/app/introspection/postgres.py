from .base import IntrospectionStrategy
from typing import Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import json

class PostgresStrategy(IntrospectionStrategy):
    async def introspect(self, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        dsn = f"postgresql+asyncpg://{connection_params['username']}:{connection_params['password']}@{connection_params['host']}:{connection_params['port']}/{connection_params['database_name']}"
        
        engine = create_async_engine(dsn)
        
        nodes = []
        edges = []
        
        async with engine.connect() as conn:
            # 1. Get Tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.scalars().all()
            
            for table in tables:
                # Get Columns
                col_result = await conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = '{table}'
                """))
                columns = [{"name": row[0], "type": row[1], "nullable": row[2]} for row in col_result]
                
                nodes.append({
                    "name": table,
                    "type": "table",
                    "metadata": json.dumps({"columns": columns})
                })
            
            # 2. Get Foreign Keys (Edges)
            fk_result = await conn.execute(text("""
                SELECT
                    tc.table_name AS source_table,
                    kcu.column_name AS source_column,
                    ccu.table_name AS target_table,
                    ccu.column_name AS target_column
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
            """))
            
            fks = fk_result.fetchall()
            for fk in fks:
                edges.append({
                    "source": fk[0],
                    "target": fk[2],
                    "type": "foreign_key",
                    "metadata": json.dumps({
                        "source_column": fk[1],
                        "target_column": fk[3]
                    })
                })
                
        await engine.dispose()
        return {"nodes": nodes, "edges": edges}
