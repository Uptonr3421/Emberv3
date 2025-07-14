#!/usr/bin/env python3
"""
Emberv3 Web UI - Frontend Interface
==================================

A modern web interface for interacting with the Emberv3 AI Assistant Framework.
Features real-time chat, system monitoring, and model management.

Usage:
    python web_ui.py
    
Access at: http://localhost:8001
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('emberv3_web_ui')

# Configuration
WEB_UI_HOST = os.getenv('WEB_UI_HOST', 'localhost')
WEB_UI_PORT = int(os.getenv('WEB_UI_PORT', 8001))
API_BASE_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', 8000)}"

# FastAPI app
app = FastAPI(
    title="Emberv3 Web UI",
    description="Web interface for Emberv3 AI Assistant Framework",
    version="1.0.0"
)

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Active connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Active connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Models
class ChatMessage(BaseModel):
    message: str
    timestamp: Optional[str] = None
    type: str = "user"  # user, assistant, system

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return get_html_content()

@app.get("/health")
async def health_check():
    """Web UI health check"""
    return {"status": "healthy", "service": "emberv3_web_ui", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_system_status():
    """Get system status from main API"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {"error": "Unable to connect to Emberv3 API"}

@app.post("/api/generate")
async def generate_text(request: GenerationRequest):
    """Generate text using the main API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=request.dict(),
            timeout=30
        )
        return response.json()
    except Exception as e:
        logger.error(f"Failed to generate text: {e}")
        raise HTTPException(status_code=500, detail="Generation failed")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Echo user message
            await manager.send_personal_message(
                json.dumps({
                    "type": "user",
                    "message": message_data["message"],
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
            
            # Generate AI response
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate",
                    json={
                        "prompt": message_data["message"],
                        "max_tokens": message_data.get("max_tokens", 500),
                        "temperature": message_data.get("temperature", 0.7)
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "assistant",
                            "message": ai_response,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                else:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "system",
                            "message": "Error: Failed to generate response",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    
            except Exception as e:
                logger.error(f"WebSocket generation error: {e}")
                await manager.send_personal_message(
                    json.dumps({
                        "type": "system",
                        "message": f"Error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def get_html_content():
    """Generate the HTML content for the web interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emberv3 AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 0;
            box-shadow: 0 0 30px rgba(0,0,0,0.1);
        }
        
        .sidebar {
            width: 300px;
            background: #2c3e50;
            color: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            font-size: 24px;
            margin-bottom: 5px;
            color: #3498db;
        }
        
        .logo p {
            font-size: 12px;
            color: #bdc3c7;
        }
        
        .status {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .status h3 {
            margin-bottom: 10px;
            color: #3498db;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 12px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #27ae60;
            margin-right: 5px;
        }
        
        .controls {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .controls h3 {
            margin-bottom: 10px;
            color: #3498db;
        }
        
        .control-group {
            margin: 10px 0;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #bdc3c7;
        }
        
        input[type="range"] {
            width: 100%;
            margin: 5px 0;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 5px;
            border: none;
            border-radius: 4px;
            background: #2c3e50;
            color: white;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #ecf0f1;
        }
        
        .chat-header {
            background: #3498db;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #ecf0f1;
        }
        
        .message {
            margin: 10px 0;
            padding: 15px;
            border-radius: 12px;
            max-width: 80%;
            position: relative;
        }
        
        .message.user {
            background: #3498db;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: white;
            color: #2c3e50;
            margin-right: auto;
            border: 1px solid #bdc3c7;
        }
        
        .message.system {
            background: #e74c3c;
            color: white;
            margin: 0 auto;
            text-align: center;
            font-size: 12px;
        }
        
        .message-time {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #bdc3c7;
        }
        
        .chat-input input {
            flex: 1;
            padding: 15px;
            border: 1px solid #bdc3c7;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        
        .chat-input button {
            margin-left: 10px;
            padding: 15px 30px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .chat-input button:hover {
            background: #2980b9;
        }
        
        .chat-input button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            padding: 10px 20px;
            color: #7f8c8d;
            font-style: italic;
            font-size: 12px;
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
                order: 2;
            }
            
            .chat-container {
                order: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">
                <h1>🔥 Emberv3</h1>
                <p>AI Assistant Framework</p>
            </div>
            
            <div class="status">
                <h3>System Status</h3>
                <div class="status-item">
                    <span><span class="status-dot"></span>API Server</span>
                    <span id="api-status">Checking...</span>
                </div>
                <div class="status-item">
                    <span><span class="status-dot"></span>Model</span>
                    <span id="model-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span><span class="status-dot"></span>WebSocket</span>
                    <span id="ws-status">Connecting...</span>
                </div>
            </div>
            
            <div class="controls">
                <h3>Generation Settings</h3>
                <div class="control-group">
                    <label for="temperature">Temperature: <span id="temp-value">0.7</span></label>
                    <input type="range" id="temperature" min="0.1" max="2.0" step="0.1" value="0.7">
                </div>
                <div class="control-group">
                    <label for="max-tokens">Max Tokens:</label>
                    <input type="number" id="max-tokens" min="50" max="2000" value="500">
                </div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-header">
                <h2>Chat with Emberv3 AI</h2>
                <p>Powered by Phi-3 Local Model</p>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message system">
                    <div>🔥 Emberv3 AI Assistant is ready to help!</div>
                    <div class="message-time">System Message</div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typing-indicator" style="display: none;">
                AI is typing...
            </div>
            
            <div class="chat-input">
                <input type="text" id="message-input" placeholder="Type your message here..." maxlength="500">
                <button id="send-button">Send</button>
            </div>
        </div>
    </div>

    <script>
        class EmberWebUI {
            constructor() {
                this.ws = null;
                this.isConnected = false;
                this.messageInput = document.getElementById('message-input');
                this.sendButton = document.getElementById('send-button');
                this.chatMessages = document.getElementById('chat-messages');
                this.typingIndicator = document.getElementById('typing-indicator');
                this.temperatureSlider = document.getElementById('temperature');
                this.maxTokensInput = document.getElementById('max-tokens');
                
                this.init();
            }
            
            init() {
                this.connectWebSocket();
                this.setupEventListeners();
                this.checkSystemStatus();
                setInterval(() => this.checkSystemStatus(), 10000); // Check every 10 seconds
            }
            
            connectWebSocket() {
                const wsUrl = `ws://${window.location.host}/ws`;
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.updateStatus('ws-status', 'Connected');
                    console.log('WebSocket connected');
                };
                
                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.addMessage(message);
                    this.hideTypingIndicator();
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;
                    this.updateStatus('ws-status', 'Disconnected');
                    console.log('WebSocket disconnected');
                    // Attempt to reconnect
                    setTimeout(() => this.connectWebSocket(), 3000);
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateStatus('ws-status', 'Error');
                };
            }
            
            setupEventListeners() {
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                this.sendButton.addEventListener('click', () => this.sendMessage());
                
                this.temperatureSlider.addEventListener('input', (e) => {
                    document.getElementById('temp-value').textContent = e.target.value;
                });
            }
            
            sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message || !this.isConnected) return;
                
                this.showTypingIndicator();
                this.messageInput.value = '';
                this.sendButton.disabled = true;
                
                const messageData = {
                    message: message,
                    max_tokens: parseInt(this.maxTokensInput.value),
                    temperature: parseFloat(this.temperatureSlider.value)
                };
                
                this.ws.send(JSON.stringify(messageData));
                
                setTimeout(() => {
                    this.sendButton.disabled = false;
                }, 1000);
            }
            
            addMessage(message) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${message.type}`;
                
                const timestamp = new Date(message.timestamp).toLocaleTimeString();
                messageDiv.innerHTML = `
                    <div>${message.message}</div>
                    <div class="message-time">${timestamp}</div>
                `;
                
                this.chatMessages.appendChild(messageDiv);
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
            
            showTypingIndicator() {
                this.typingIndicator.style.display = 'block';
            }
            
            hideTypingIndicator() {
                this.typingIndicator.style.display = 'none';
            }
            
            updateStatus(elementId, status) {
                document.getElementById(elementId).textContent = status;
            }
            
            async checkSystemStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    if (data.error) {
                        this.updateStatus('api-status', 'Error');
                        this.updateStatus('model-status', 'Unknown');
                    } else {
                        this.updateStatus('api-status', 'Online');
                        this.updateStatus('model-status', data.model_info?.model_name || 'Active');
                    }
                } catch (error) {
                    this.updateStatus('api-status', 'Offline');
                    this.updateStatus('model-status', 'Offline');
                }
            }
        }
        
        // Initialize the web UI when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new EmberWebUI();
        });
    </script>
</body>
</html>
    """

def main():
    """Main entry point for the web UI server"""
    logger.info("🌐 Starting Emberv3 Web UI...")
    logger.info(f"📡 Web UI will be available at: http://{WEB_UI_HOST}:{WEB_UI_PORT}")
    logger.info(f"🔗 API Backend: {API_BASE_URL}")
    
    try:
        uvicorn.run(
            app,
            host=WEB_UI_HOST,
            port=WEB_UI_PORT,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Web UI server stopped by user")
    except Exception as e:
        logger.error(f"❌ Web UI server error: {e}")

if __name__ == "__main__":
    main()