
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

📋 **Prerequisites**

- Docker or Python 3.6+
- A Skype account

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
   docker run -d --name skype-message-api -p 8000:8000 -v skype-api-keys:/app/db skype-message-api
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

Docker:
- Add a new API key: `docker exec -it skype-message-api python /app/utils/api_key_manager.py --add`
- Remove an API key: `docker exec -it skype-message-api python /app/utils/api_key_manager.py --remove [key]`
- Verify an API key: `docker exec -it skype-message-api python /app/utils/api_key_manager.py --check [key]`

Manual:
- Add a new API key: `python src/utils/api_key_manager.py --add`
- Remove an API key: `python src/utils/api_key_manager.py --remove [key]`
- Verify an API key: `python src/utils/api_key_manager.py --check [key]`

🚀 **Usage**

Send a custom message to a Skype group using the `/send-custom-message` endpoint. Example with cURL:
(Manual method is listening on the port 5000)
```bash
curl -X POST http://localhost:8000/send-custom-message      -H 'Content-Type: application/json'      -H 'x-api-key: YOUR_API_KEY'      -d '{"group_id": "your_group_id_here", "message": "Your custom message here"}'
```

👐 **Contributing**

Contributions, issues, and feature requests are welcome. Feel free to check our issues page.

📜 **License**

Distributed under the MIT License. See LICENSE for more information.

📬 **Contact**

Laszlo A. Toth - lavx@lavx.hu
Project Link: https://github.com/LavX/SkypeMessageAPI
