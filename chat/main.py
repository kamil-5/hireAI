from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import ChatOllama
from langchain.schema import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
import uvicorn

# Initialiser FastAPI
app = FastAPI()

# Ajouter middleware pour CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacez "*" par l'URL de votre frontend en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du modèle et de l'historique
llm = ChatOllama(model="llama3:latest", temperature=0.5)
memory = ChatMessageHistory()

# Route pour afficher la page HTML avec le CSS intégré
@app.get("/", response_class=HTMLResponse)
def serve_chat_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Chatbot</title>
        <style>
            /* Style pour l'interface utilisateur */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #e0f7fa, #ffffff);
            }
            .chat-container {
                width: 400px;
                height: 600px;
                border-radius: 10px;
                background: white;
                display: flex;
                flex-direction: column;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            .chat-header {
                background: #0078d7;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 20px;
                font-weight: bold;
            }
            .chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f4f4f4;
            }
            .message {
                margin: 10px 0;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 70%;
                word-wrap: break-word;
                font-size: 14px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            }
            .message.user {
                background: #0078d7;
                color: white;
                align-self: flex-end;
            }
            .message.bot {
                background: #e8e8e8;
                align-self: flex-start;
            }
            .chat-input {
                display: flex;
                padding: 10px;
                border-top: 1px solid #ddd;
                background: white;
            }
            .chat-input input {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .chat-input button {
                padding: 12px 15px;
                margin-left: 10px;
                background: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">AI Chatbot</div>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Type your message here..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        <script>
            const chatMessages = document.getElementById('chatMessages');

            function addMessage(content, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', sender);
                messageDiv.textContent = content;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the latest message
            }

            async function sendMessage() {
                const userInput = document.getElementById('userInput');
                const message = userInput.value.trim();
                if (!message) return;

                // Afficher le message de l'utilisateur
                addMessage(message, 'user');
                userInput.value = '';

                try {
                    const response = await fetch('/chat/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ user_message: message }),
                    });

                    if (!response.ok) {
                        throw new Error('Erreur avec la connexion au serveur.');
                    }

                    const data = await response.json();
                    addMessage(data.bot_message, 'bot');
                } catch (error) {
                    addMessage("Erreur : Impossible de contacter le serveur.", 'bot');
                    console.error(error);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Route API pour gérer les messages
@app.post("/chat/")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("user_message", "")
    context = data.get("context", "")

    try:
        # Ajouter la question de l'utilisateur à l'historique
        memory.add_message(HumanMessage(content=user_message))

        # Obtenir la réponse du modèle
        response = llm.invoke(memory.messages)

        # Ajouter la réponse à l'historique
        if isinstance(response, AIMessage):
            bot_message = response.content
            memory.add_message(response)
        else:
            bot_message = "Je suis désolé, je n'ai pas compris votre demande."

        return {"bot_message": bot_message, "context": context}
    except Exception as e:
        return {"bot_message": f"Erreur : {str(e)}", "context": context}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
