from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import os

# Import routes from api folder
from api.routes import auth, buyer, manufacturer, tasks, calendar, file_upload, quotation, proforma_invoice

# Import database
from database.connection import init_db, seed_admin

# Initialize FastAPI
app = FastAPI(
    title="Business Management API",
    description="Complete business management system with Google Drive integration",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    print("Application starting up...")
    db_success = await init_db()
    if db_success:
        await seed_admin()
        print("Application ready!")
    else:
        print("Application started with database errors. Some endpoints may fail.")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(buyer.router, prefix="/api/buyers", tags=["Buyers"])
app.include_router(manufacturer.router, prefix="/api/manufacturers", tags=["Manufacturers"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(file_upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(quotation.router, prefix="/api/quotation", tags=["Quotation"])
app.include_router(proforma_invoice.router, prefix="/api/proforma", tags=["Proforma Invoice"])

# Root endpoint - Redirect to frontend
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# Global exception handler to prevent HTML error pages on Vercel
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Business Management API is running",
        "version": "1.0.0"
    }

def setup_logging():
    """Configure logging to both console and file, specifically capturing uvicorn output"""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Check if we're running on Vercel
    is_vercel = os.getenv("VERCEL") == "1"
    
    if not is_vercel:
        log_file = 'server.log'
        try:
            # File handler (5MB per file, max 3 files)
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)
            
            # Specific loggers for uvicorn
            for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
                log = logging.getLogger(logger_name)
                log.addHandler(file_handler)
                log.setLevel(logging.INFO)
            
            print(f"Logging initialized. Check {os.path.abspath(log_file)} for logs.")
        except Exception as e:
            print(f"Could not initialize file logging: {e}. Falling back to console only.")
    else:
        print("Running on Vercel - File logging disabled.")
    
    # Ensure console logging is always available (standard for serverless)
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

if __name__ == "__main__":
    setup_logging()
    print("=" * 70)
    print("BUSINESS MANAGEMENT API")
    print("=" * 70)
    print("Server URLs:")
    print("   Frontend: http://127.0.0.1:8000")
    print("   Login:    http://127.0.0.1:8000/static/index.html")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("   ReDoc:    http://127.0.0.1:8000/redoc")
    print("\nDefault Superuser Credentials:")
    print("   Admin: admin1 / admin123")
    print("\nFeatures:")
    print("   [+] User Authentication & Role Management")
    print("   [+] Buyer Management")
    print("   [+] Manufacturer Management")
    print("   [+] Task Management")
    print("   [+] Calendar System")
    print("   [+] File Upload (Local + Google Drive)")
    print("\n" + "=" * 70)
    print("Press CTRL+C to stop the server")
    print("=" * 70 + "\n")

    
    # Choose one:
    
    # Option 1: Localhost only
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
    # Option 2: Network accessible (original)
    # uvicorn.run(app, host="0.0.0.0", port=8000)