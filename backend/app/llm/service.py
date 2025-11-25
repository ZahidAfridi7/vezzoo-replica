import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import create_engine, text
from .. import models
from ..routers.connections import decrypt_password

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, api_key=self.api_key)

    async def generate_response(self, message: str, connection_id: int, db: AsyncSession) -> dict:
        # 1. Fetch Connection Details
        result = await db.execute(select(models.Connection).where(models.Connection.id == connection_id))
        conn = result.scalars().first()
        if not conn:
            raise ValueError("Connection not found")

        # 2. Prepare Database Connection for LangChain
        # LangChain's SQLDatabase typically uses a sync engine. 
        # We create a temporary sync engine for this request.
        password = decrypt_password(conn.encrypted_password)
        db_url = f"postgresql://{conn.username}:{password}@{conn.host}:{conn.port}/{conn.database_name}"
        
        try:
            # Create engine and SQLDatabase wrapper
            # We use a sync engine here because LangChain's SQL tools are primarily sync-first or wrap sync engines.
            # For high-concurrency async apps, we might want to run this in a threadpool if it blocks too much,
            # but for this implementation, direct execution is acceptable.
            engine = create_engine(db_url)
            sql_db = SQLDatabase(engine)

            # 3. Create SQL Generation Chain
            # We can customize the prompt if needed, but the default is usually good.
            # We explicitly ask for just the SQL to be returned.
            
            chain = create_sql_query_chain(self.llm, sql_db)
            
            # 4. Generate SQL
            # ainvoke allows async invocation of the chain
            response_sql = await chain.ainvoke({"question": message})
            
            # Clean up SQL (sometimes it wraps in markdown)
            cleaned_sql = response_sql.replace("```sql", "").replace("```", "").strip()
            
            # 5. Execute SQL
            # We execute using the same engine (or we could use the async engine from before, but we have this one handy)
            # Since we are in an async function, we should ideally use async execution.
            # However, `engine.connect()` is sync. 
            # Let's use the sql_db.run method which is convenient, or execute manually.
            # sql_db.run(cleaned_sql) returns a string representation. We might want raw data.
            
            with engine.connect() as connection:
                cursor = connection.execute(text(cleaned_sql))
                keys = cursor.keys()
                rows = cursor.fetchall()
                data = [dict(zip(keys, row)) for row in rows]

            return {
                "role": "assistant",
                "content": f"Here are the results:\n\nQuery: `{cleaned_sql}`",
                "sql_query": cleaned_sql,
                "data": data
            }

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"Error processing request: {str(e)}",
                "sql_query": None
            }
        finally:
            # Ensure engine is disposed
            if 'engine' in locals():
                engine.dispose()
