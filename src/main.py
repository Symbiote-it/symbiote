from pathlib import Path
from src.agent import DeepSeekClient
from src.db import session_manager, init_db


def main():
    # Initialize database tables (safe to call multiple times)
    init_db()
    
    # Create a new chat session
    chat_id = session_manager.create_chat()
    print(f"Created chat session: {chat_id}")
    
    # Initialize the agent client
    client = DeepSeekClient()

    description = """
        Create comprehensive test instruction for Write a test for testing GitHub repository search functionality
    """
    website_url = "https://github.com"
    
    # Get action from agent (uses database-backed session)
    test_code = client.get_action(chat_id=chat_id, website_url=website_url, description=description)
    print(test_code)
    
    # You can check chat info
    info = session_manager.get_chat_info(chat_id)
    print(f"\nChat info: {info}")


if __name__ == "__main__":
    main()
