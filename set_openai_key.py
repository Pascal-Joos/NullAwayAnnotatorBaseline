import os


def main():
    
    print("Please provide your OpenAI API-KEY.")
    openai_api_key = input("OpenAI API-KEY: ").strip()

    # Write the mini-SWE-agent configuration file
    with open("/home/vscode/.config/mini-swe-agent/.env", 'w') as file:
        file.write(f"""MSWEA_MODEL_NAME='openai/gpt-5.1'
OPENAI_API_KEY='{openai_api_key}'
MSWEA_CONFIGURED='true'
""")



    # Add OPENAI_API_KEY to .env file
    file_paths = [".env"]

    for file_path in file_paths:
        with open(file_path, 'w+') as file:
            file.write("OPENAI_API_KEY=" + openai_api_key)


if __name__ == "__main__":
    main()