#!/usr/bin/env python3
"""
Ember FastAPI Server
Provides REST API endpoints for the Ember system
"""

import os
import time
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

# Load our custom modules
from model_manager import ModelManager
from agents.file_monitor import FileMonitor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Ember AI Assistant API",
    description="Advanced AI Assistant Framework with Local and Remote LLM Support",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model_manager: Optional[ModelManager] = None
file_monitor: Optional[FileMonitor] = None

# Pydantic Models
class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for generation")
    max_tokens: Optional[int] = Field(4096, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")
    top_p: Optional[float] = Field(0.9, description="Top-p value for generation")

class GenerationResponse(BaseModel):
    response: str = Field(..., description="The generated response")
    model_used: str = Field(..., description="The model that generated the response")
    generation_time: float = Field(..., description="Time taken to generate response")
    tokens_generated: Optional[int] = Field(None, description="Number of tokens generated")

class SystemStatus(BaseModel):
    status: str
    uptime: str
    model_manager: Dict[str, Any]
    file_monitor: Dict[str, Any]
    system_resources: Dict[str, Any]

class ModelInfo(BaseModel):
    local_model_loaded: bool
    openai_client_loaded: bool
    config: Dict[str, Any]
    system_resources: Dict[str, Any]

# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global model_manager, file_monitor
    
    print("🚀 Starting Ember API Server...")
    
    # Initialize model manager
    model_manager = ModelManager()
    if model_manager.initialize():
        print("✅ Model Manager initialized")
    else:
        print("❌ Model Manager initialization failed")
    
    # Initialize file monitor
    file_monitor = FileMonitor()
    file_monitor.start_monitoring()
    print("✅ File Monitor started")
    
    print("🎯 Ember API Server ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global file_monitor
    
    print("🔄 Shutting down Ember API Server...")
    
    if file_monitor:
        file_monitor.stop_monitoring()
        print("✅ File Monitor stopped")
    
    print("👋 Ember API Server shutdown complete")

# Dependency to get model manager
def get_model_manager() -> ModelManager:
    if model_manager is None or not model_manager.is_initialized:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return model_manager

def get_file_monitor() -> FileMonitor:
    if file_monitor is None:
        raise HTTPException(status_code=503, detail="File monitor not initialized")
    return file_monitor

# API Endpoints

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Ember AI Assistant API",
        "version": "3.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "status": "/status",
            "generate": "/generate",
            "model_info": "/model/info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "model_manager": model_manager is not None and model_manager.is_initialized,
            "file_monitor": file_monitor is not None and file_monitor.is_running
        }
    }

@app.get("/status", response_model=SystemStatus)
async def get_system_status(
    mm: ModelManager = Depends(get_model_manager),
    fm: FileMonitor = Depends(get_file_monitor)
):
    """Get comprehensive system status"""
    start_time = getattr(app.state, 'start_time', time.time())
    uptime = time.time() - start_time
    
    def format_uptime(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    return SystemStatus(
        status="running",
        uptime=format_uptime(uptime),
        model_manager=mm.get_model_info(),
        file_monitor=fm.get_statistics(),
        system_resources=mm._check_system_resources()
    )

@app.get("/model/info", response_model=ModelInfo)
async def get_model_info(mm: ModelManager = Depends(get_model_manager)):
    """Get detailed model information"""
    info = mm.get_model_info()
    return ModelInfo(**info)

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    mm: ModelManager = Depends(get_model_manager)
):
    """Generate text using the available model"""
    try:
        start_time = time.time()
        
        # Generate response
        response = mm.generate(
            request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        generation_time = time.time() - start_time
        
        # Determine which model was used
        model_used = "local" if mm.local_model else "openai"
        
        return GenerationResponse(
            response=response,
            model_used=model_used,
            generation_time=generation_time,
            tokens_generated=len(response.split()) if response else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/generate/stream")
async def generate_text_stream(
    request: GenerationRequest,
    mm: ModelManager = Depends(get_model_manager)
):
    """Generate text with streaming response (basic implementation)"""
    try:
        async def generate_stream():
            response = mm.generate(
                request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )
            
            # Simulate streaming by yielding words
            words = response.split()
            for word in words:
                yield f"data: {json.dumps({'word': word, 'done': False})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect
            
            yield f"data: {json.dumps({'word': '', 'done': True})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming generation failed: {str(e)}")

@app.get("/files/status")
async def get_file_status(fm: FileMonitor = Depends(get_file_monitor)):
    """Get file monitoring status"""
    return fm.get_statistics()

@app.get("/files/changes")
async def get_recent_changes(
    limit: int = 50,
    fm: FileMonitor = Depends(get_file_monitor)
):
    """Get recent file changes"""
    changes = list(fm.change_queue.items())[-limit:]
    return {
        "changes": [
            {
                "file_path": path,
                "relative_path": info["relative_path"],
                "event_type": info["event_type"],
                "timestamp": info["timestamp"],
                "processed": info["processed"]
            }
            for path, info in changes
        ],
        "total_changes": len(fm.change_queue)
    }

@app.post("/admin/reload")
async def reload_system(mm: ModelManager = Depends(get_model_manager)):
    """Reload the model manager (admin endpoint)"""
    try:
        success = mm.initialize()
        return {
            "success": success,
            "message": "Model manager reloaded successfully" if success else "Failed to reload model manager",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

@app.get("/admin/stats")
async def get_admin_stats(
    mm: ModelManager = Depends(get_model_manager),
    fm: FileMonitor = Depends(get_file_monitor)
):
    """Get detailed admin statistics"""
    return {
        "model_manager": mm.get_model_info(),
        "file_monitor": fm.get_statistics(),
        "system": mm._check_system_resources(),
        "project_state": {
            "files_tracked": len(fm.project_state.get('files', {})),
            "last_scan": fm.project_state.get('last_scan'),
            "version": fm.project_state.get('version')
        }
    }

# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "path": str(request.url.path),
            "available_endpoints": [
                "/", "/health", "/status", "/generate", "/model/info", "/docs"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def main():
    """Main function to run the server"""
    # Store start time
    app.state.start_time = time.time()
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🔥 Starting Ember API Server on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 Debug Mode: {debug}")
    
    # Run the server
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info",
        access_log=debug
    )

if __name__ == "__main__":
    main()