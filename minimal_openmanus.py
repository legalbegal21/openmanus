#!/usr/bin/env python3
"""
Minimal OpenManus Implementation with only the essentials
"""

import os
import sys
import toml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
from loguru import logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    logger.error("Anthropic SDK not found. Please install with: pip install anthropic")
    sys.exit(1)

class MinimalOpenManus:
    """A simplified version of OpenManus that works with minimal dependencies"""
    
    def __init__(self, config_path: str = "config/config.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.api_key = self.config["llm"]["api_key"]
        self.model = self.config["llm"]["model"]
        self.client = Anthropic(api_key=self.api_key)
        
        logger.info(f"MinimalOpenManus initialized with model: {self.model}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found at {self.config_path.absolute()}")
            sys.exit(1)
        
        try:
            config = toml.load(self.config_path)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def run(self, user_input: str) -> str:
        """Process user input and return agent response"""
        try:
            logger.info("Sending request to Claude...")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.config["llm"].get("max_tokens", 4096),
                temperature=self.config["llm"].get("temperature", 0.0),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant specializing in providing detailed responses to legal queries, particularly in immigration law. When addressing legal matters, ensure responses are comprehensive and well-structured."
                    },
                    {"role": "user", "content": user_input}
                ]
            )
            
            response = message.content[0].text
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"Error: {str(e)}"

def main():
    """Main function to run the minimal OpenManus agent"""
    agent = MinimalOpenManus()
    
    print("\n==== MinimalOpenManus Agent ====")
    print("(Type 'exit' to quit)\n")
    
    while True:
        try:
            user_input = input("\nYour query: ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                print("Please enter a valid query.")
                continue
            
            print("\nProcessing your request...\n")
            response = agent.run(user_input)
            print(f"Response:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\nOperation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()