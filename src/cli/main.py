from src.utils import get_logger
from src.db import session_manager, init_db, MessageRole

logger = get_logger(__name__)

class CommandLineInterface:
    def process_request(self, user_request):
        """Main pipeline to process user request: request -> plan -> execute"""
        logger.info(f"Processing: {user_request}")
        chat_id = session_manager.create_chat()
        session_manager.add_message(chat_id, MessageRole.USER, user_request)

    def interactive_mode(self):
        """Interactive CLI for symbiote"""
        logger.info("Symbiote Ready to work...")
        logger.info("Type 'quit' to exit")

        while True:
            request = input("\nWhat should I do? > ")
            if request.lower() in ['quit', 'exit', 'q']:
                break
            
            self.process_request(user_request=request)


def main():
    """Entry point for the symbiote CLI."""
    # Initialize DB setup
    init_db()

    # Start interactive CLI shell
    cli = CommandLineInterface()
    cli.interactive_mode()


if __name__ == "__main__":
    main()
