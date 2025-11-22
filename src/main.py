from src.agent import Model, DockerOllamaClient

def main():
    client = DockerOllamaClient()

    test_code = client.generate(
        description="Write a test for testing GitHub repository search functionality",
        model=Model.PHI3_MINI
    )
    print("Test result: as below")
    print(test_code)

if __name__ == "__main__":
    main()
