from pathlib import Path
import json
from typing import Any, Dict, Optional
import logging


class SettingsManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.settings_dir = data_dir / "settings"
        self.settings_dir.mkdir(exist_ok=True)

        # Default settings for each category
        self.defaults = {
            "generation": {
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "context_length": 4096,
                "memory_window": 10,
                "stop_sequences": [],
            },
            "autonomy": {
                "autonomous_mode": False,
                "confidence_threshold": 0.85,
                "file_operations": False,
                "network_access": False,
                "system_commands": False,
                "max_autonomous_turns": 5,
                "user_confirmation_timeout": 30,
            },
            "messages": {
                "message_style": "professional",
                "max_message_length": 2000,
                "use_markdown": True,
                "auto_reply": False,
                "typing_speed": "natural",
                "response_delay": 500,
                "greeting_message": "Hi! I'm your AI assistant. How can I help you today?",
                "error_message": "I apologize, but I encountered an error. Please try again.",
                "farewell_message": "Thank you for chatting with me. Have a great day!",
            },
            "voice": {
                "voice_id": "en-US-Neural2-A",
                "speaking_rate": 1.0,
                "pitch": 0,
                "enable_voice_input": False,
                "language": "en-US",
                "sensitivity": 75,
                "wake_word": "Hey Nugget",
                "idle_timeout": 30,
                "continuous_listening": False,
            },
            "files": {
                "root_directory": "~/nugget-workspace",
                "allow_file_creation": False,
                "allow_file_modification": False,
                "allowed_types": ["text", "code"],
                "custom_extensions": "",
                "max_file_size": 10,
                "create_backups": True,
                "backup_retention": 30,
            },
            "agent": {
                "agent_mode": "assistant",
                "personality": "professional",
                "learn_from_interactions": False,
                "skills": ["code_analysis", "debugging", "documentation", "testing"],
                "advanced_features": [],
                "memory_capacity": 512,
                "knowledge_update_interval": 24,
                "persistent_memory": True,
            },
        }

    def _get_settings_path(self, nugget_id: str, category: str) -> Path:
        """Get the path to a settings file for a specific nugget and category."""
        return self.settings_dir / nugget_id / f"{category}.json"

    def get_settings(self, nugget_id: str, category: str) -> Dict[str, Any]:
        """Get settings for a specific nugget and category."""
        settings_path = self._get_settings_path(nugget_id, category)

        if not settings_path.exists():
            # Return defaults if no settings file exists
            return self.defaults.get(category, {})

        try:
            with open(settings_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error reading settings for {nugget_id}/{category}: {e}")
            return self.defaults.get(category, {})

    def save_settings(
        self, nugget_id: str, category: str, settings: Dict[str, Any]
    ) -> bool:
        """Save settings for a specific nugget and category."""
        settings_path = self._get_settings_path(nugget_id, category)
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving settings for {nugget_id}/{category}: {e}")
            return False

    def reset_settings(self, nugget_id: str, category: str) -> Dict[str, Any]:
        """Reset settings to defaults for a specific nugget and category."""
        defaults = self.defaults.get(category, {})
        self.save_settings(nugget_id, category, defaults)
        return defaults

    def validate_api_key(self, key: str, service: str) -> bool:
        """Validate an API key for a specific service."""
        # TODO: Implement actual API key validation logic
        if not key:
            return False

        if service == "openai":
            return key.startswith("sk-")
        elif service == "anthropic":
            return key.startswith("sk-ant-")
        elif service == "gemini":
            return key.startswith("AIza")

        return False
