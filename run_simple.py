#!/usr/bin/env python3
"""
Simplified script to test OpenManus functionality
"""

import os
import sys
import asyncio
import toml
from pathlib import Path

# Load configuration
try:
    config_path = Path("config/config.toml")
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path.absolute()}")
        sys.exit(1)
    
    config = toml.load(config_path)
    print("Configuration loaded successfully:")
    print(f"  Model: {config['llm']['model']}")
    print(f"  API URL: {config['llm']['base_url']}")
    print(f"  API Key: {config['llm']['api_key'][:8]}...{config['llm']['api_key'][-4:]}")
except Exception as e:
    print(f"Error loading configuration: {e}")
    sys.exit(1)

# Set up the API environment
os.environ["ANTHROPIC_API_KEY"] = config["llm"]["api_key"]

async def main():
    try:
        # Import the LLM client
        from anthropic import Anthropic
        client = Anthropic(api_key=config["llm"]["api_key"])
        
        # Test the connection
        print("\nTesting connection to Anthropic API...")
        message = client.messages.create(
            model=config["llm"]["model"],
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello! Are you working?"}
            ]
        )
        
        print("\nAPI test successful. Response:")
        print(message.content[0].text)
        
        print("\nSetup is complete. You can now use OpenManus.")
        
    except Exception as e:
        print(f"Error testing API connection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())