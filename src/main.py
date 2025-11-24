from src.agent import Model, DockerOllamaClient

def main():
    client = DockerOllamaClient()

    prompt = f"""
        Create comprehensive test instruction for Write a test for testing GitHub repository search functionality

        Requirement:
        - Give instruction in YAML format only
    """
    test_code = client.generate(
        prompt,
        model=Model.PHI3_MINI
    )
    print(test_code)

if __name__ == "__main__":
    main()
