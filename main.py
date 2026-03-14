from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes from api folder
from api.routes import auth, buyer, manufacturer, tasks, calendar, file_upload, quotation, proforma_invoice

# Import database
from database.connection import init_db

# Initialize FastAPI
app = FastAPI(
    title="Business Management API",
    description="Complete business management system with Google Drive integration",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    await init_db()

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

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Business Management API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 BUSINESS MANAGEMENT API")
    print("=" * 70)
    print("\n📍 Server URLs:")
    print("   Frontend: http://127.0.0.1:8000")
    print("   Login:    http://127.0.0.1:8000/static/index.html")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("   ReDoc:    http://127.0.0.1:8000/redoc")
    print("\n🔐 Default Login Credentials:")
    print("   Admin: admin1 / admin123")
    print("   User:  user1 / user123")
    print("\n✨ Features:")
    print("   ✅ User Authentication")
    print("   ✅ Buyer Management")
    print("   ✅ Manufacturer Management")
    print("   ✅ Task Management")
    print("   ✅ Calendar System")
    print("   ✅ File Upload (Local + Google Drive)")
    print("\n" + "=" * 70)
    print("🛑 Press CTRL+C to stop the server")
    print("=" * 70 + "\n")
    
    # Choose one:
    
    # Option 1: Localhost only
    uvicorn.run(app, host="127.0.0.1", port=5000)
    
    # Option 2: Network accessible (original)
    # uvicorn.run(app, host="0.0.0.0", port=8000)