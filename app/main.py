from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Import routers and middleware
from app.api import users
from app.api import profiles
from app.api import nfc
from app.core.auth import supabase_auth
from app.core.error_handling import ContactsException
from app.core.config import settings

# Load environment variables
load_dotenv()


def create_app() -> FastAPI:
    """
    Application factory function
    """
    app = FastAPI(
        title="Contacts Backend",
        description="Privacy-first social networking platform backend",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure global exception handlers
    @app.exception_handler(ContactsException)
    async def custom_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # Include routers
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
    app.include_router(nfc.router, prefix="/api/nfc", tags=["nfc"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """
        Comprehensive health check endpoint
        """
        return {
            "status": "healthy",
            "version": "0.1.0",
            "supabase_connected": supabase_auth.supabase is not None,
        }

    return app


# Create the app instance
app = create_app()
