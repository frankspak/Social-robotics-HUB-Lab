from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
from naoqi import ALProxy
from tinyllama.client import TinyLlamaClient
from oaichat.oaiclient import OaiClient
import socket
from optparse import OptionParser

PEPPER_IP = "192.168.1.140"
PORT = 9559

hostname = socket.gethostname()
ip_address_host = socket.gethostbyname(hostname)
print(ip_address_host)

parser = OptionParser()
parser.add_option("--server",
                  help="Server to use (tinyllama or openai).",
    dest="server")
parser.set_defaults(server='openai')

# Create an instance of FastAPI
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

def create_conversation(texts):
    html = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=1280, user-scalable=no" />
            <title>WhatsApp Conversation</title>
            <script>
                async function sendText() {

                    let textbox = document.getElementById("inputText");
                    const text = textbox.value;
                    textbox.value = '';
                    let messageBody = document.querySelector('.chat-body');

                    let newMessageHTML = `
                        <div class="message sent">
                        <span class="message-text">` + text + `</span>
                    </div>`;

                    messageBody.insertAdjacentHTML('afterbegin', newMessageHTML);

                    const url = "http://127.0.0.1:5000/send-input";

                    try {
                        const response = await fetch(url, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({ "text_input": text })
                        });

                        const data = await response.json();
                        const answer = data.answer; 

                        let newResponseHTML = `
                            <div class="message received">
                            <span class="message-text">` + answer + `</span>
                        </div>`;

                        messageBody.insertAdjacentHTML('afterbegin', newResponseHTML);                        
                    } catch (error) {
                        console.error("Error:", error);
                    }
                }
            </script>
            <style>

                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    background-color: #ece5dd;
                }

                .chat-window {
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    background-color: #fff;
                    display: flex;
                    flex-direction: column;
                }

                .chat-body {
                    flex: 1;
                    padding: 15px;
                    background-color: #e5ddd5;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                }

                .message {
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 10px;
                    position: relative;
                    display: block;
                    clear: both; /* Ensures no overlapping */
                    max-width: 75%;
                    word-wrap: break-word; /* Prevents long words from overflowing */
                }

                .message.received {
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-bottom-left-radius: 0;
                    align-self: flex-end;
                }

                .message.sent {
                    background-color: #DCF8C6;
                    border-bottom-right-radius: 0;
                    align-self: flex-start;
                }

                .message-text {
                    font-size: 3vw;
                }

                .chat-input-container {
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                    background-color: #f0f0f0;
                    border-top: 1px solid #e0e0e0;
                }

                .chat-input {
                    flex-grow: 1;
                    padding: 10px;
                    border: none;
                    border-radius: 20px;
                    background-color: #fff;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    font-size: 16px;
                    resize: none;
                    outline: none;
                    margin-right: 10px;
                }

                .send-button {
                    padding: 10px 20px;
                    background-color: #25d366;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
                }

                .send-button:active {
                    transform: scale(0.95);
                }

                .chat-input-container,
                .chat-input,
                .send-button {
                    height: 40px;
                    max-height: 40px;
                }
            </style>
        </head>
        <body>
            <div class="chat-window">

                <div class="chat-body">
    """
    texts.reverse()
    for message in texts:
        message_class = "sent" if message["sender"] == "sent" else "received"
        html += "<div class=\"message " + message_class + """\">
            <span class="message-text">""" + message['message'] + """</span>
        </div>"""
    html += """
                    <div class="chat-input-container">
                        <textarea class="chat-input" placeholder="Type a message" id="inputText"></textarea>
                        <button class="send-button" onclick="sendText()">Send</button>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    return html

# Define the route for the home page
@app.route("/")
def home():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    html = create_conversation(texts)
    return render_template_string(html)

@app.route("/send-input", methods= ["POST"])
def send_input():
    with open("conversation.json", "r+") as f:
        texts = json.load(f)
    data = request.get_json()
    text_input = data.get("text_input")
    print(text_input)
    # tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)

    texts.append({
        "message": text_input,
        "sender": "sent"
    })
    with open("conversation.json", "w+") as f:
        json.dump(texts, f)

    answer = chatbot.respond(text_input)
    texts.append({
        "message":  answer,
        "sender": "received"
    })
    # tts.say(answer)

    with open("conversation.json", "w+") as f:
        json.dump(texts, f)

    return jsonify({"answer":answer})


# Run the app (when using uvicorn)
if __name__ == "__main__":
    (opts, args_) = parser.parse_args()
    participantId = input('Participant ID: ')
    if opts.server == 'tinyllama':
        chatbot = TinyLlamaClient(user=participantId)
    else:
        chatbot = OaiClient(user=participantId)

    app.run(host='0.0.0.0', port=5000, debug=False)
