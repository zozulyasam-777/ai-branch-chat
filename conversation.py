"""
conversation.py
Core logic for managing non-linear dialogue branches.
Handles JSON storage, branching logic, and AI provider abstraction.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from anonymizer import SimpleAnonymizer

class ConversationManager:
    """
    Manages the state of a branching conversation.
    Stores data in a JSON tree structure where each node has a parent_id.
    """
    
    def __init__(self, session_file: str):
        self.session_file = session_file
        self.config = config or {}        
        self.data = self._load_or_create_session()
        self.current_branch = self.data.get("meta", {}).get("current_branch", "main")

        # Initialize anonymizer
        privacy_config = self.config.get('privacy', {})
        session_id = privacy_config.get('session_id', 'default')
        self.anonymizer = SimpleAnonymizer(privacy_config)
        self.session_id = session_id

    def _load_or_create_session(self) -> Dict:
        """
        Loads existing session JSON or creates a new one if missing.
        """
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Initialize new session structure
            return {
                "meta": {
                    "title": "New Session",
                    "created_at": datetime.now().isoformat(),
                    "current_branch": "main"
                },
                "branches": {
                    "main": {
                        "forked_from": None,
                        "nodes": []
                    }
                }
            }

    def save(self):
        """
        Persists the current state to the JSON file.
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_node(self, role: str, content: str, branch: Optional[str] = None) -> str:
        """
        Adds a new message node to the current branch.
        Returns the node_id.
        """
        if branch is None:
            branch = self.current_branch

        if branch not in self.data["branches"]:
            raise ValueError(f"Branch '{branch}' does not exist.")

        nodes = self.data["branches"][branch]["nodes"]
        
        # Determine parent_id (the last node in this branch)
        parent_id = nodes[-1]["id"] if nodes else None
        
        new_node = {
            "id": str(uuid.uuid4())[:8],  # Short unique ID
            "parent_id": parent_id,
            "role": role,                 # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        
        nodes.append(new_node)
        self.save()
        return new_node["id"]

    def fork_branch(self, new_branch_name: str):
        """
        Creates a new branch starting from the current state.
        Copies the history up to the current point.
        """
        if new_branch_name in self.data["branches"]:
            raise ValueError(f"Branch '{new_branch_name}' already exists.")
        
        # Copy the current branch's nodes to the new one
        # In a real Git-like system, we might copy by reference, 
        # but for JSON simplicity, we duplicate the list.
        current_nodes = self.data["branches"][self.current_branch]["nodes"]
        
        self.data["branches"][new_branch_name] = {
            "forked_from": self.current_branch,
            "nodes": [node.copy() for node in current_nodes]
        }
        self.current_branch = new_branch_name
        self.data["meta"]["current_branch"] = self.current_branch
        self.save()

    def switch_branch(self, branch_name: str):
        """
        Switches the active context to an existing branch.
        """
        if branch_name not in self.data["branches"]:
            raise ValueError(f"Branch '{branch_name}' does not exist.")
        
        self.current_branch = branch_name
        self.data["meta"]["current_branch"] = self.current_branch
        self.save()

    def get_context_for_ai(self) -> List[Dict]:
        """
        Prepares the message history for the AI API.
        Only returns nodes from the current branch lineage.
        """
        nodes = self.data["branches"][self.current_branch]["nodes"]
        # Format for standard Chat API (e.g., OpenAI)
        return [{"role": n["role"], "content": n["content"]} for n in nodes]

    def export_feed(self, output_path: str):
        """
        Exports the conversation to JSON Feed format for publishing.
        """
        feed_items = []
        # Flatten all branches for the feed
        for branch_name, branch_data in self.data["branches"].items():
            for node in branch_data["nodes"]:
                item = {
                    "id": node["id"],
                    "title": f"[{branch_name}] {node['role']}",
                    "content_text": node["content"],
                    "date_published": node["timestamp"],
                    "tags": [f"branch:{branch_name}", f"role:{node['role']}"]
                }
                feed_items.append(item)
        
        # Sort by timestamp
        feed_items.sort(key=lambda x: x["date_published"])

        feed_json = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": self.data["meta"]["title"],
            "items": feed_items
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feed_json, f, indent=2, ensure_ascii=False)

    def add_node(self, role: str, content: str, branch: Optional[str] = None, 
                 metadata: Optional[Dict] = None) -> str:
        """
        Adds a new message node to the current branch.
        Now includes anonymization metadata.
        """
        if branch is None:
            branch = self.current_branch

        if branch not in self.data["branches"]:
            raise ValueError(f"Branch '{branch}' does not exist.")

        nodes = self.data["branches"][branch]["nodes"]
        parent_id = nodes[-1]["id"] if nodes else None
        
        # Anonymize content if enabled
        anon_content = content
        token_map = {}
        
        if self.config.get('privacy', {}).get('enabled', False):
            anon_content, token_map = self.anonymizer.anonymize(content, self.session_id)
        
        new_node = {
            "id": str(uuid.uuid4())[:8],
            "parent_id": parent_id,
            "role": role,
            "content": content,              # Original (for local storage)
            "content_anon": anon_content,    # Anonymized (for AI API)
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "token_map": token_map           # For reverse mapping
        }
        
        nodes.append(new_node)
        self.save()
        return new_node["id"]
    
    def get_context_for_ai(self, anonymized: bool = True) -> List[Dict]:
        """
        Prepares the message history for the AI API.
        
        Args:
            anonymized: If True, return anonymized content; else original
        """
        nodes = self.data["branches"][self.current_branch]["nodes"]
        context = []
        
        for n in nodes:
            content_key = "content_anon" if anonymized else "content"
            context.append({
                "role": n["role"],
                "content": n.get(content_key, n["content"])
            })
        
        return context
    
    def deanonymize_response(self, text: str) -> str:
        """
        Restore original values in AI response.
        """
        if not self.config.get('privacy', {}).get('enabled', False):
            return text
        return self.anonymizer.deanonymize(text, self.session_id)
    
    def get_privacy_stats(self) -> Dict:
        """
        Get anonymization statistics for current session.
        """
        return self.anonymizer.get_stats(self.session_id)