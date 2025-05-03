FROM python:3.12-slim

WORKDIR /app/OpenManus

# Install system dependencies including browser requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install pip and uv
RUN pip install --upgrade pip && pip install uv

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Install playwright browsers
RUN pip install playwright && python -m playwright install chromium

# Copy the application
COPY . .

# Create a script to run OpenManus in Docker
RUN echo '#!/usr/bin/env python3\n\
import os\n\
import asyncio\n\
from app.agent.manus import Manus\n\
from app.logger import logger\n\
\n\
async def run_manus():\n\
    """Run the Manus agent in a loop for Docker"""  \n\
    agent = Manus()\n\
    try:\n\
        print("\\n==== OpenManus AI Agent (Docker Version) ====\\n")\n\
        print("Enter your instructions. Type \'exit\' to quit.\\n")\n\
        \n\
        while True:\n\
            prompt = input("Enter your instructions: ")\n\
            if prompt.lower() in ["exit", "quit"]:\n\
                break\n\
            if not prompt.strip():\n\
                logger.warning("Empty prompt provided.")\n\
                continue\n\
            \n\
            logger.warning("Processing your request...")\n\
            print("\\nAgent is working on your request...\\n")\n\
            \n\
            await agent.run(prompt)\n\
            \n\
            logger.info("Request processing completed.")\n\
            print("\\nTask completed! You can enter a new task or type \'exit\' to quit.\\n")\n\
    \n\
    except KeyboardInterrupt:\n\
        logger.warning("Operation interrupted by user.")\n\
        print("\\nOperation interrupted. Cleaning up...")\n\
    except Exception as e:\n\
        logger.error(f"Error running Manus agent: {str(e)}")\n\
        print(f"\\nAn error occurred: {str(e)}")\n\
    finally:\n\
        # Clean up browser if needed\n\
        await agent.available_tools.get_tool("browser_use").cleanup()\n\
    \n\
    return\n\
\n\
if __name__ == "__main__":\n\
    try:\n\
        asyncio.run(run_manus())\n\
    except KeyboardInterrupt:\n\
        print("\\nExiting OpenManus...")\n\
    except Exception as e:\n\
        print(f"Fatal error: {str(e)}")\n\
' > run_openmanus_docker.py && chmod +x run_openmanus_docker.py

# Update the config file to use the right max_tokens for Opus
RUN sed -i 's/max_tokens = 8192/max_tokens = 4096/' config/config.toml

# Expose port for potential API access
EXPOSE 8080

# Default command
CMD ["python3", "run_openmanus_docker.py"]