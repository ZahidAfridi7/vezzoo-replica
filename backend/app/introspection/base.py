from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncEngine

class IntrospectionStrategy(ABC):
    @abstractmethod
    async def introspect(self, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connects to the database and returns a dictionary representing the schema graph.
        Return format:
        {
            "nodes": [
                {"name": "table_name", "type": "table", "metadata": {...}},
                ...
            ],
            "edges": [
                {"source": "table_a", "target": "table_b", "type": "foreign_key", "metadata": {...}},
                ...
            ]
        }
        """
        pass
