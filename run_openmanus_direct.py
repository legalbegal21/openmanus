#!/usr/bin/env python3
"""
Direct OpenManus Runner
This script directly imports and runs the Manus agent, bypassing any potential import issues
"""

import asyncio
import sys
from pathlib import Path

# Ensure we have access to the app module
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the components directly with relative paths
from app.agent.manus import Manus
from app.logger import logger

async def run_manus():
    """Run the Manus agent directly"""
    agent = Manus()
    try:
        print("\n==== OpenManus AI Agent (Claude 3 Opus) ====")
        print("Type your instructions below. The agent will use browser automation and other tools to assist you.\n")
        
        prompt = input("Enter your instructions: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return
        
        logger.warning("Processing your request...")
        print("\nAgent is working on your request...\n")
        
        await agent.run(prompt)
        
        logger.info("Request processing completed.")
        print("\nTask completed! You can enter a new task or press Ctrl+C to exit.")
    
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        print("\nOperation interrupted. Cleaning up...")
        # Clean up browser if needed
        await agent.available_tools.get_tool("browser_use").cleanup()
    except Exception as e:
        logger.error(f"Error running Manus agent: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
    
    return

if __name__ == "__main__":
    try:
        asyncio.run(run_manus())
    except KeyboardInterrupt:
        print("\nExiting OpenManus...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)