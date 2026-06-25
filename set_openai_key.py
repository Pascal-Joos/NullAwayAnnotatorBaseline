import os


def get_user_account_home():
    return os.path.expanduser("~")

def main():
    
    print("Please provide your OpenAI API-KEY.")
    openai_api_key = input("OpenAI API-KEY: ").strip()

    # Write the mini-SWE-agent configuration file
    print(f"Writing mini-SWE-agent configuration file to {get_user_account_home()}/.config/mini-swe-agent/.env")
    if not os.path.exists(get_user_account_home() + "/.config/mini-swe-agent"):
        os.makedirs(get_user_account_home() + "/.config/mini-swe-agent")

    with open(get_user_account_home() + "/.config/mini-swe-agent/.env", 'w') as file:
        file.write(f"""MSWEA_MODEL_NAME='openai/gpt-5.1'
OPENAI_API_KEY='{openai_api_key}'
MSWEA_CONFIGURED='true'
""")



    # Add OPENAI_API_KEY to .env file
    file_paths = [".env"]

    for file_path in file_paths:
        with open(file_path, 'w') as file:
            print(f"Writing OPENAI_API_KEY to {file_path}")
            file.write("OPENAI_API_KEY=" + openai_api_key)


if __name__ == "__main__":
    main()