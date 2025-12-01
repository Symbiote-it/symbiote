import uuid
from pathlib import Path
from src.agent import Model, Phi3Client, LlavaClient, DeepSeekClient

def main():
    client = DeepSeekClient()

    description = f"""
        Create comprehensive test instruction for Write a test for testing GitHub repository search functionality
    """
    # Get the absolute path to the image
    project_root = Path(__file__).parent.parent.absolute()
    image_path = str(project_root / "test_image" / "github_1.png")
    website_url = "https://github.com"
    
    test_code = client.get_action(session_id=uuid.uuid4(), website_url=website_url, description=description)
    print(test_code)

if __name__ == "__main__":
    main()
