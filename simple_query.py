#!/usr/bin/env python3
"""
Immigration Law Query Interface for Anthropic API
Enhanced with immigration-specific templates and features
"""

import os
import sys
import toml
import json
import textwrap
from pathlib import Path
import argparse
from datetime import datetime

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    print("Anthropic SDK not found. Please install with: pip install anthropic")
    sys.exit(1)

# Immigration law-specific templates
TEMPLATES = {
    "1": {
        "name": "I-601A Waiver Requirements",
        "query": "What are the requirements for an I-601A provisional waiver? Include eligibility criteria, documentation needed, and common reasons for approval."
    },
    "2": {
        "name": "DACA Requirements and Updates",
        "query": "What are the current DACA requirements and status? Include the latest updates on the program and renewal process."
    },
    "3": {
        "name": "Prosecutorial Discretion Request",
        "query": "What factors should be emphasized in a prosecutorial discretion request to OPLA? Include the most persuasive humanitarian factors and how to structure the request."
    },
    "4": {
        "name": "Asylum Timeline and Process",
        "query": "What is the current asylum application process and timeline? Include key forms, interview preparation advice, and current processing times."
    },
    "5": {
        "name": "Naturalization Eligibility",
        "query": "What are the requirements for naturalization? Include continuous residence, physical presence, and good moral character requirements."
    },
    "6": {
        "name": "Immigration Court Proceedings",
        "query": "Explain the immigration court process from NTA to individual hearing. Include key motions, relief options, and preparation strategies."
    },
    "7": {
        "name": "Family-Based Petitions",
        "query": "Explain the family-based immigration petition process. Include forms, waiting times, and priority dates for different family relationships."
    }
}

# Enhanced system prompt for immigration law
IMMIGRATION_SYSTEM_PROMPT = """
You are a specialized legal assistant focusing on U.S. immigration law. When responding:

1. Structure responses clearly with headings, subheadings, and bullet points where appropriate.
2. Cite relevant statutes, regulations, and case law (e.g., INA sections, CFR references, BIA decisions).
3. Distinguish between agency guidance (USCIS memos, policy manual) and binding legal authority.
4. Identify potential pitfalls or complications.
5. Mention relevant forms with their proper designations (e.g., I-601A, I-130, I-485).
6. Be precise about timelines, filing locations, and procedural requirements.
7. Focus on practical advice that an immigration attorney could immediately apply.
8. Note significant circuit splits or jurisdictional differences where relevant.
9. Frame responses to be favorable to the immigrant/petitioner where multiple interpretations exist.
10. Highlight humanitarian factors that may strengthen discretionary applications.

Remember that you're assisting an immigration attorney who needs accurate, comprehensive information to advise clients properly.
"""

def load_config(config_path):
    """Load configuration from TOML file"""
    config_path = Path(config_path)
    if not config_path.exists():
        print(f"Config file not found at {config_path.absolute()}")
        sys.exit(1)
    
    try:
        config = toml.load(config_path)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def save_response(query, response):
    """Save query and response to a file for later reference"""
    responses_dir = Path("./responses")
    responses_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"response_{timestamp}.md"
    filepath = responses_dir / filename
    
    with open(filepath, "w") as f:
        f.write(f"# Immigration Law Query - {timestamp}\n\n")
        f.write(f"## Query\n\n{query}\n\n")
        f.write(f"## Response\n\n{response}\n")
    
    print(f"\nResponse saved to {filepath}")
    return filepath

def query_claude(query, config, system_prompt=None, save=True):
    """Send a query to Claude and return the response"""
    client = Anthropic(api_key=config["llm"]["api_key"])
    
    if system_prompt is None:
        system_prompt = IMMIGRATION_SYSTEM_PROMPT
    
    try:
        print("\nSending request to Claude...\n")
        
        message = client.messages.create(
            model=config["llm"]["model"],
            max_tokens=config["llm"].get("max_tokens", 4096),
            temperature=config["llm"].get("temperature", 0.0),
            system=system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        
        response = message.content[0].text
        
        if save:
            save_response(query, response)
            
        return response
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return f"Error: {str(e)}"

def display_templates():
    """Display available query templates"""
    print("\n==== Immigration Law Query Templates ====\n")
    for key, template in TEMPLATES.items():
        print(f"{key}. {template['name']}")
    print("\n0. Custom Query")
    print("\nType the number of the template you want to use, or 0 for a custom query.")

def format_response(response):
    """Format the response for better readability in the terminal"""
    # Split into lines and apply minimal formatting
    lines = response.split('\n')
    formatted = []
    
    for line in lines:
        if line.startswith('#'):  # Heading
            formatted.append(f"\n\033[1m{line}\033[0m")  # Bold
        elif line.startswith('*') or line.startswith('-'):  # List item
            formatted.append(f"  {line}")  # Indent list items
        else:
            # Wrap long paragraphs
            if len(line) > 80:
                wrapped = textwrap.fill(line, width=80)
                formatted.append(wrapped)
            else:
                formatted.append(line)
    
    return '\n'.join(formatted)

def main():
    parser = argparse.ArgumentParser(description="Immigration Law Query Interface for Anthropic API")
    parser.add_argument("query", nargs="?", help="Query to send to Claude (in quotes)")
    parser.add_argument("--config", default="config/config.toml", help="Path to config file")
    parser.add_argument("--template", type=str, help="Use a specific template by number")
    parser.add_argument("--save", action="store_true", help="Save the response to a file")
    parser.add_argument("--no-save", action="store_false", dest="save", help="Don't save the response")
    parser.set_defaults(save=True)
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    # Check if a specific template was requested
    if args.template and args.template in TEMPLATES:
        query = TEMPLATES[args.template]["query"]
        print(f"Using template: {TEMPLATES[args.template]['name']}")
        response = query_claude(query, config, save=args.save)
        print(f"\nResponse:\n\n{format_response(response)}")
        return
    
    if args.query:
        # Direct query mode
        response = query_claude(args.query, config, save=args.save)
        print(f"\nResponse:\n\n{format_response(response)}")
    else:
        # Interactive mode with templates
        print("\n==== Immigration Law Assistant ====")
        
        display_templates()
        choice = input("\nYour choice: ").strip()
        
        if choice in TEMPLATES:
            # Use selected template
            query = TEMPLATES[choice]["query"]
            print(f"\nUsing template: {TEMPLATES[choice]['name']}")
        elif choice == "0":
            # Custom query
            query = input("\nYour custom query: ")
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                return
                
            if not query.strip():
                print("Please enter a valid query.")
                return
        else:
            print("Invalid choice. Please select a valid template number.")
            return
        
        response = query_claude(query, config, save=args.save)
        print(f"\nResponse:\n\n{format_response(response)}")

if __name__ == "__main__":
    main()