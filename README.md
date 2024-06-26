
# SkypeMessageAPI

🚀 **Overview**

SkypeMessageAPI is a Python Flask 🐍 application designed to provide a seamless integration point for third-party applications to send messages to Skype groups. It supports Docker for easy deployment and scalability.

📝 **Description**

This API leverages the `skpy` library to interact with Skype, allowing users to programmatically send custom messages to specified group chats. It features a secure API key management system to authenticate requests, making it ideal for automating notifications or alerts within teams or groups.

🌟 **Features**

- 🤖 Send automated messages to Skype group chats.
- 🔐 API key authentication for secure access.
- 📋 Easy integration with third-party applications.
- 🐳 Docker support for easy deployment and scalability.
- 🧠 Advanced AI message handling for dynamic reply processing.
- 💾 MongoDB integration for robust message logging (AI messaging). (optional)
- ⚙️ Enhanced API Key Management for a more user-friendly access control.

📋 **Prerequisites**

- Docker or Python 3.6+
- A Skype account
- MongoDB (optional)

🔑 **Registering a Skype Account**

To use SkypeMessageAPI, you must have a Skype account. If you don't have one, visit the Skype website to create an account. Once set up, update the `.env` file with your Skype credentials.

📋 **Gathering Skype Groups**

Use `list_groups.py` to list and gather the Skype group IDs required for notifications.

🛠 **Installation & Setup**

**Using Docker (Recommended)**
1. **Clone the Repository**
   ```
   git clone https://github.com/LavX/SkypeMessageAPI.git
   cd SkypeMessageAPI/
   ```
2. **Create .env**
   Create a `.env` file in the project root with your Skype credentials.
   Ensure the `.env` file follows the provided example format.
   ```
   cd src
   cp .env_example .env
   nano .env
   ```
3. **Build the Docker Image**
   ```
   cd ..
   docker build -t skype-message-api .
   ```
4. **Run the Container**
   ```
   docker run -d --name skype-message-api -p 5000:5000 -v skype-api-keys:/app/db skype-message-api
   ```

**Without Docker**
1. **Clone the Repository**
   ```
   git clone https://github.com/LavX/SkypeMessageAPI.git
   cd SkypeMessageAPI/
   ```
2. **Set Up a Virtual Environment**
   - Create a virtual environment:
     ```
     python -m venv .venv
     ```
   - Activate the virtual environment:
     ```
     source .venv/bin/activate
     ```
3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```
4. **Create .env**
   Create a `.env` file in the project /src with your Skype credentials.
   Ensure the `.env` file follows the provided example format.
   ```
   cd src
   cp .env_example .env
   nano .env
   ```
5. **Launch app.py**
   ```
   python app.py
   ```

⚙️ **API Key Management**

- Add a new API key: `docker exec -it skype-message-api python -m utils.api_key_manager --add`
- Remove an API key: `docker exec -it skype-message-api python -m utils.api_key_manager --remove [key]`
- Verify an API key: `docker exec -it skype-message-api python -m utils.api_key_manager --check [key]`

For manual setups without Docker, use the following commands in the project's root directory:
- `python -m utils.api_key_manager --add`
- `python -m utils.api_key_manager --remove [key]`
- `python -m utils.api_key_manager --check [key]`


**🧠 Activating the AI Messaging Endpoint**

Activating the AI messaging endpoint in your SkypeMessageAPI application involves integrating AI-driven functionalities to enable dynamic, intelligent responses from Skype's Bing AI, particularly useful for automated interactions or support systems. This guide details the setup and utilization of the `ai_message` endpoint.

 Prerequisites for AI Messaging

- Ensure your environment is correctly set up as described in the Installation & Setup section.
- A functioning MongoDB instance is optional but recommended for logging AI interactions and API key management.

**Configuring the Environment for AI Messaging**

1. **Skype Credentials**: Your `.env` file should include your Skype account credentials (`SKYPE_USERNAME` and `SKYPE_PASSWORD`). These credentials allow the application to log into Skype and send messages.

2. **AI Messaging Group ID**: The `GROUP_ID` environment variable must contain the ID of the Skype group where AI-driven messages will be sent. Use the `list_groups.py` script to find and set this ID.

3. **MongoDB Configuration (Optional)**:
   - Enable MongoDB logging by setting `ENABLE_MONGODB` to `true`. This enables the application to log messages and manage API keys.
   - Fill in your MongoDB connection details (`MONGODB_URI`, `MONGODB_DB_NAME`, `MONGODB_USERNAME`, and `MONGODB_PASSWORD`) for database connectivity.
   - System using 'api_keys' and 'messages' collections

**Activating and Using the AI Messaging Endpoint**

The `ai_message` endpoint is operational once your `.env` file is set up, and your environment is ready (via Docker or manual setup). This endpoint facilitates sending messages to the designated group and, if enabled, logs these interactions in MongoDB.

- **Logging**: If MongoDB logging is enabled, interactions through the AI messaging endpoint will be logged. This is beneficial for auditing and debugging.

**Customizing AI Responses with** `instruction.txt`

To further customize how the AI responds to messages, you can edit the `instruction.txt` file located in the project's root directory. This file should contain instructions or guidelines that the AI will follow when generating responses. For example, you can specify tone, style, or specific information that the AI should include or avoid in its responses. Adjusting the contents of `instruction.txt` allows for greater control over the AI's interaction patterns and can be modified as needed to refine responses.

🚀 **Usage**

- **Sending Custome Messages:** To send a custom message to a Skype group, use the `/send-custom-message` endpoint.
    ```json
    {
        "group_id": "ID of the recipient",
        "message": "Hello, how can I help you today?"
    }
    ```

- **Sending AI Messages**: Make a POST request to `/send-ai-message` with a JSON payload including `message` and `session_id`. The `session_id` is crucial for maintaining conversation context with the AI.

    ```json
    {
        "message": "Hello, how can I help you today?",
        "session_id": "unique_session_identifier"
    }
    ```

👐 **Contributing**

Contributions, issues, and feature requests are welcome. For more information on how to contribute, please check our issues page.

📜 **License**

Distributed under the MIT License. See LICENSE for more information.

📬 **Contact**

Laszlo A. Toth - lavx@lavx.hu
Project Link: https://github.com/LavX/SkypeMessageAPI

## Disclaimer

This project is intended for educational purposes only and might violate Skype's or Microsoft's Terms and Conditions. Users should ensure they comply with all relevant policies and regulations when using or deploying this project. The author(s) do not assume any responsibility for any misuse or breach of agreement on the part of the users.
