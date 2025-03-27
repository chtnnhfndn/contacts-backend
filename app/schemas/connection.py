from pydantic import BaseModel, Field
from datetime import datetime
from app.models.models import ConnectionType


class ConnectionCreate(BaseModel):
    """Schema for creating a connection"""

    connected_user_id: int
    connection_type: ConnectionType


class ConnectionResponse(BaseModel):
    """Schema for returning connection details"""

    id: int
    connected_user_id: int
    connection_type: ConnectionType
    created_at: datetime


class ConnectionRequest(BaseModel):
    """Schema for incoming connection requests"""

    requester_id: int
    connection_type: ConnectionType = Field(
        default=ConnectionType.ACQUAINTANCE,
        description="Default connection type if not specified",
    )
