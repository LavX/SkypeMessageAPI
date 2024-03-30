
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

🚀 **Usage**

To send a custom message to a Skype group, use the `/send-custom-message` endpoint. Additionally, to leverage the AI messaging feature, send a POST request to `/send-ai-message` with the required JSON payload including `message` and `session_id`.

👐 **Contributing**

Contributions, issues, and feature requests are welcome. For more information on how to contribute, please check our issues page.

📜 **License**

Distributed under the MIT License. See LICENSE for more information.

📬 **Contact**

Laszlo A. Toth - lavx@lavx.hu
Project Link: https://github.com/LavX/SkypeMessageAPI
