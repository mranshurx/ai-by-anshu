import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Single-page HTML/CSS/JS frontend built directly into the app
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRouter Free AI Chat</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121212; color: #e0e0e0; margin: 0; display: flex; height: 100vh; }
        aside { width: 280px; background: #1e1e1e; border-right: 1px solid #333; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        main { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        header { padding: 15px 20px; background: #1e1e1e; border-bottom: 1px solid #333; font-weight: bold; }
        #chat-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 8px; line-height: 1.5; word-wrap: break-word; }
        .user-message { background: #6366f1; color: white; align-self: flex-end; }
        .ai-message { background: #2a2a2a; color: #e0e0e0; align-self: flex-start; border: 1px solid #333; }
        .input-area { padding: 20px; background: #1e1e1e; border-top: 1px solid #333; display: flex; gap: 10px; }
        input[type="password"], select, input[type="text"] { width: 100%; padding: 10px; background: #2a2a2a; border: 1px solid #333; color: white; border-radius: 6px; box-sizing: border-box; }
        button { padding: 0 20px; background: #6366f1; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <aside>
        <h2>⚡ Settings</h2>
        <div>
            <label>OpenRouter API Key:</label>
            <input type="password" id="apiKey" placeholder="sk-or-v1-...">
        </div>
        <div>
            <label>Select Free Model:</label>
            <select id="modelSelect">
                <option value="openrouter/free">Auto Free Router</option>
                <option value="qwen/qwen3.8-27b:free">Qwen 27B (Free)</option>
                <option value="nvidia/nemotron-3.5-lightning:free">Nvidia Nemotron 3.5 (Free)</option>
            </select>
        </div>
    </aside>
    <main>
        <header>OpenRouter Web UI</header>
        <div id="chat-container">
            <div class="message ai-message">Hello! Enter your OpenRouter API key on the left and say something.</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type a message..." onkeydown="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </main>
    <script>
        const chatContainer = document.getElementById('chat-container');
        let messageHistory = [];

        async function sendMessage() {
            const apiKey = document.getElementById('apiKey').value.trim();
            const model = document.getElementById('modelSelect').value;
            const inputField = document.getElementById('userInput');
            const userText = inputField.value.trim();

            if (!apiKey) { alert("Please enter your API key!"); return; }
            if (!userText) return;

            appendMessage(userText, 'user-message');
            messageHistory.push({ role: "user", content: userText });
            inputField.value = "";

            const aiDiv = appendMessage("Thinking...", 'ai-message');

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey, model, messages: messageHistory })
                });
                const data = await res.json();
                
                if (data.error) {
                    aiDiv.textContent = "Error: " + data.error;
                } else {
                    aiDiv.textContent = data.reply;
                    messageHistory.push({ role: "assistant", content: data.reply });
                }
            } catch (err) {
                aiDiv.textContent = "Network error: " + err.message;
            }
        }

        function appendMessage(text, className) {
            const div = document.createElement('div');
            div.className = `message ${className}`;
            div.textContent = text;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return div;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def proxy_chat():
    data = request.json
    api_key = data.get("apiKey")
    model = data.get("model")
    messages = data.get("messages")

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com",
                "X-Title": "OpenRouter Web UI"
            },
            json={
                "model": model,
                "messages": messages
            },
            timeout=30
        )
        res_json = response.json()
        if "error" in res_json:
            return jsonify({"error": res_json["error"].get("message", "Unknown API error")})
        
        reply = res_json["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
