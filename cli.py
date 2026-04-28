#!/usr/bin/env python3
"""
cli.py
Command Line Interface for AI Branching Chat.
Allows users to chat, fork branches, and export data.
"""

import sys
import json
import os
from conversation import ConversationManager

# Try to import Rich for nice UI, fallback to print if missing
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    console = Console()
    USE_RICH = True
except ImportError:
    USE_RICH = False

class MockAIProvider:
    """
    Simulates an AI response for testing without API keys.
    In production, replace this with OpenAI/Anthropic client.
    """
    def generate(self, context):
        last_message = context[-1]["content"] if context else "Hello"
        
        # Simple logic to simulate the medical test case
        if "symptoms" in last_message.lower() or "head" in last_message.lower():
            return "Based on your symptoms, it could be ORVI or Flu. Shall we explore ORVI first?"
        elif "orvi" in last_message.lower():
            return "For ORVI, check your throat and keep a temperature diary. Drink plenty of fluids."
        elif "flu" in last_message.lower():
            return "Flu usually starts suddenly with high fever. Rest is crucial. Check saturation."
        else:
            return "I understand. Let's continue exploring this branch."

class ChatInterface:
    def __init__(self, session_file="data/session.json"):
        self.manager = ConversationManager(session_file)
        self.ai = MockAIProvider()
        self.print("🌿 AI Branching Chat v0.1 started")
        self.print(f"📂 Loaded session: {session_file}")
        self.print(f"🌲 Current branch: [bold]{self.manager.current_branch}[/bold]" if USE_RICH else f"Current branch: {self.manager.current_branch}")

    def print(self, text):
        if USE_RICH:
            console.print(text)
        else:
            print(text)

    def loop(self):
        """
        Main interaction loop.
        """
        while True:
            try:
                # Get user input
                prompt = f"[{self.manager.current_branch}] > "
                user_input = input(prompt)
                
                if not user_input.strip():
                    continue

                # Handle Commands
                if user_input.startswith("/"):
                    self.handle_command(user_input)
                else:
                    # Normal Chat Flow
                    self.process_message(user_input)

            except KeyboardInterrupt:
                self.print("\n👋 Goodbye!")
                break
            except Exception as e:
                self.print(f"❌ Error: {e}")

    def handle_command(self, cmd: str):
        """
        Parses special commands starting with '/'.
        """
        parts = cmd.split()
        command = parts[0].lower()

        if command == "/fork":
            if len(parts) < 2:
                self.print("Usage: /fork <branch_name>")
                return
            name = parts[1]
            self.manager.fork_branch(name)
            self.print(f"✅ Created and switched to branch: {name}")

        elif command == "/switch":
            if len(parts) < 2:
                self.print("Usage: /switch <branch_name>")
                return
            name = parts[1]
            self.manager.switch_branch(name)
            self.print(f"✅ Switched to branch: {name}")

        elif command == "/export":
            path = "web/feed.json"
            self.manager.export_feed(path)
            self.print(f"✅ Exported JSON Feed to {path}")

        elif command == "/exit":
            sys.exit(0)
        
        else:
            self.print(f"❓ Unknown command: {command}")

    def process_message(self, text: str):
        """
        Sends message to AI and saves response.
        """
        # 1. Save User Message
        self.manager.add_node("user", text)
        if USE_RICH:
            self.print(f"[bold blue]You:[/bold blue] {text}")
        else:
            print(f"You: {text}")

        # 2. Get Context & Generate AI Response
        context = self.manager.get_context_for_ai()
        response = self.ai.generate(context)

        # 3. Save AI Message
        self.manager.add_node("assistant", response)
        if USE_RICH:
            self.print(f"[bold green]AI:[/bold green] {response}")
        else:
            print(f"AI: {response}")

if __name__ == "__main__":
    # Initialize and start
    chat = ChatInterface()
    chat.loop()