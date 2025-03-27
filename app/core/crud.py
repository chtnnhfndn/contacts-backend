from supabase import create_client
from typing import Dict, Any, Optional, List
from app.core.config import settings


class SupabaseCRUD:
    def __init__(self, table_name: str):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.table_name = table_name

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in the specified table
        """
        try:
            response = self.supabase.table(self.table_name).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise ValueError(f"Error creating record: {str(e)}")

    async def read(
        self, query: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Read records from the table with optional filtering
        """
        try:
            if query:
                # Apply filters if query is provided
                response = (
                    self.supabase.table(self.table_name)
                    .select("*")
                    .match(query)
                    .execute()
                )
            else:
                response = self.supabase.table(self.table_name).select("*").execute()
            return response.data
        except Exception as e:
            raise ValueError(f"Error reading records: {str(e)}")

    async def update(
        self, id_column: str, id_value: Any, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a record by its ID
        """
        try:
            response = (
                self.supabase.table(self.table_name)
                .update(update_data)
                .eq(id_column, id_value)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise ValueError(f"Error updating record: {str(e)}")

    async def delete(self, id_column: str, id_value: Any) -> bool:
        """
        Delete a record by its ID
        """
        try:
            response = (
                self.supabase.table(self.table_name)
                .delete()
                .eq(id_column, id_value)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            raise ValueError(f"Error deleting record: {str(e)}")

    async def delete_many(self, id_column: str, id_value: Any) -> bool:
        """
        Delete multiple records by matching column value
        """
        try:
            response = (
                self.supabase.table(self.table_name)
                .delete()
                .eq(id_column, id_value)
                .execute()
            )
            # Return true if any records were deleted
            return len(response.data) >= 0
        except Exception as e:
            raise ValueError(f"Error deleting records: {str(e)}")

    async def get_by_id(
        self, id_column: str, id_value: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single record by its ID
        """
        try:
            response = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq(id_column, id_value)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise ValueError(f"Error retrieving record: {str(e)}")
