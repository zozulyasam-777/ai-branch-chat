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
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)        
        self.manager = ConversationManager(session_file)
        self.ai = MockAIProvider()")
        self.print("🌿 AI Branching Chat v0.1 started")
        self.print(f"📂 Loaded session: {session_file}")
        self.print(f"🌲 Current branch: [bold]{self.manager.current_branch}[/bold]" if USE_RICH else f"Current branch: {self.manager.current_branch}")

        # Show privacy status
        if self.config.get('privacy', {}).get('enabled', False):
            strategy = self.config.get('privacy', {}).get('mask_strategy', 'token')
            self.print(f"🔒 Privacy: ENABLED (strategy: {strategy})")
        else:
            self.print(f"🔓 Privacy: DISABLED")


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

        elif command == "/privacy":
            # Toggle or show privacy status
            if len(parts) < 2:
                current = self.config.get('privacy', {}).get('enabled', False)
                self.print(f"Privacy: {'ENABLED' if current else 'DISABLED'}")
                self.print("Usage: /privacy on|off|stats")
                return
            
            action = parts[1].lower()
            if action == 'on':
                self.config['privacy']['enabled'] = True
                self.print("✅ Privacy enabled")
            elif action == 'off':
                self.config['privacy']['enabled'] = False
                self.print("✅ Privacy disabled")
            elif action == 'stats':
                stats = self.manager.get_privacy_stats()
                self.print(f"📊 Anonymized entities: {stats['total_entities']}")
                for entity_type, count in stats.get('by_type', {}).items():
                    self.print(f"   - {entity_type}: {count}")
            else:
                self.print("❓ Unknown action. Use: on, off, stats")

        elif command == "/testanon":
            # Test anonymization without sending to AI
            if len(parts) < 2:
                self.print("Usage: /testanon <text>")
                return
            test_text = ' '.join(parts[1:])
            anon_text, token_map = self.manager.anonymizer.anonymize(test_text, self.manager.session_id)
            self.print(f"Original: {test_text}")
            self.print(f"Anonymized: {anon_text}")
            self.print(f"Tokens: {token_map}")

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

        # 2. Get Context (anonymized) & Generate AI Response
        context = self.manager.get_context_for_ai(anonymized=True)
        response_anon = self.ai.generate(context)

        # 3. Deanonymize AI Response
        response = self.manager.deanonymize_response(response_anon)

        # 4. Save AI Message
        self.manager.add_node("assistant", response)
        if USE_RICH:
            self.print(f"[bold green]AI:[/bold green] {response}")
        else:
            print(f"AI: {response}")

if __name__ == "__main__":
    # Initialize and start
    chat = ChatInterface()
    chat.loop()