#!/usr/bin/env python3
"""
Emberv3 AI Assistant - Hugging Face Spaces Deployment
Gradio interface for the uncensored Jordan-7B model
"""

import gradio as gr
import os
import sys
import threading
import time
import requests
from typing import Optional

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Emberv3 components
from model_manager_linux import ModelManagerLinux
from api_server import app as fastapi_app
import uvicorn

class EmberGradioInterface:
    def __init__(self):
        self.model_manager = None
        self.api_server_running = False
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the Emberv3 system"""
        try:
            # Initialize model manager
            self.model_manager = ModelManagerLinux()
            if self.model_manager.initialize():
                print("✅ Jordan-7B model loaded successfully")
            else:
                print("❌ Failed to load Jordan-7B model")
                
            # Start FastAPI server in background
            self.start_api_server()
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
    
    def start_api_server(self):
        """Start FastAPI server in background thread"""
        def run_server():
            uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        self.api_server_running = True
        print("✅ FastAPI server started on port 8000")
    
    def generate_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate response using Jordan-7B model"""
        try:
            if not self.model_manager:
                return "❌ Model not loaded. Please wait for system initialization."
            
            # Generate response
            response = self.model_manager.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response
            
        except Exception as e:
            return f"❌ Generation failed: {str(e)}"
    
    def get_model_info(self) -> str:
        """Get model information"""
        try:
            if not self.model_manager:
                return "Model not loaded"
            
            info = self.model_manager.get_model_info()
            return f"""
**Model**: {info.get('name', 'Unknown')}
**Status**: {info.get('status', 'Unknown')}
**Generations**: {info.get('total_generations', 0)}
**Uptime**: {info.get('uptime', 'Unknown')}
"""
        except Exception as e:
            return f"Error getting model info: {str(e)}"

# Initialize the interface
ember_interface = EmberGradioInterface()

# Create Gradio interface
with gr.Blocks(title="🔥 Emberv3 AI Assistant - Jordan-7B", theme=gr.themes.Default()) as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>🔥 Emberv3 AI Assistant</h1>
        <h3>Powered by Uncensored Jordan-7B Model</h3>
        <p><strong>⚠️ Warning:</strong> This is an uncensored AI model with no content restrictions</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat with Jordan-7B",
                height=500,
                show_label=True
            )
            
            msg = gr.Textbox(
                label="Your message",
                placeholder="Enter your message here...",
                lines=2,
                max_lines=10
            )
            
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear Chat")
        
        with gr.Column(scale=1):
            # Settings panel
            gr.HTML("<h3>⚙️ Settings</h3>")
            
            max_tokens = gr.Slider(
                label="Max Tokens",
                minimum=50,
                maximum=2048,
                value=512,
                step=50
            )
            
            temperature = gr.Slider(
                label="Temperature",
                minimum=0.1,
                maximum=1.0,
                value=0.7,
                step=0.1
            )
            
            # Model info
            gr.HTML("<h3>📊 Model Info</h3>")
            model_info = gr.Textbox(
                label="Model Status",
                value=ember_interface.get_model_info(),
                lines=6,
                interactive=False
            )
            
            refresh_btn = gr.Button("Refresh Info")
    
    # Chat functionality
    def respond(message, history, max_tokens, temperature):
        if not message.strip():
            return history, ""
        
        # Add user message to history
        history.append([message, "Thinking..."])
        
        # Generate response
        response = ember_interface.generate_response(
            prompt=message,
            max_tokens=int(max_tokens),
            temperature=temperature
        )
        
        # Update history with response
        history[-1][1] = response
        
        return history, ""
    
    def clear_chat():
        return [], ""
    
    def refresh_model_info():
        return ember_interface.get_model_info()
    
    # Event handlers
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, max_tokens, temperature],
        outputs=[chatbot, msg]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot, max_tokens, temperature],
        outputs=[chatbot, msg]
    )
    
    clear_btn.click(clear_chat, outputs=[chatbot, msg])
    refresh_btn.click(refresh_model_info, outputs=[model_info])

# Launch the interface
if __name__ == "__main__":
    print("🚀 Starting Emberv3 AI Assistant...")
    print("🔥 Jordan-7B model loading...")
    print("🌐 Gradio interface launching...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=False
    )