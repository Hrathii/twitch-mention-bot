# --- Webserver-Teil, damit Render "Web Service" akzeptiert ---
from flask import Flask
import threading
import os
import socket
import requests
from dotenv import load_dotenv

app = Flask('')

@app.route('/')
def home():
    return "Twitch bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = threading.Thread(target=run)
t.start()

# --- Ab hier: Dein normaler Botcode ---

load_dotenv()  # .env-Datei laden

# Aus Umgebungsvariablen laden
NICK = os.getenv("TWITCH_NICK")
CHANNELS = os.getenv("TWITCH_CHANNELS").split(",")
WATCHED_NAME = os.getenv("WATCHED_NAME")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
IRC_TOKEN = os.getenv("IRC_TOKEN")

# Twitch IRC-Server
server = "irc.chat.twitch.tv"
port = 6667

# Socket-Verbindung zu Twitch
sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {IRC_TOKEN}\n".encode("utf-8"))
sock.send(f"NICK {NICK}\n".encode("utf-8"))

# Channels beitreten
for channel in CHANNELS:
    sock.send(f"JOIN #{channel.strip()}\n".encode("utf-8"))

print("Bot läuft und hört auf Nachrichten...")

def send_to_discord(message):
    if DISCORD_WEBHOOK:
        try:
            data = {"content": message}
            requests.post(DISCORD_WEBHOOK, json=data)
        except Exception as e:
            print("Fehler beim Senden an Discord:", e)

buffer = ""
while True:
    try:
        buffer += sock.recv(2048).decode("utf-8")
        lines = buffer.split("\r\n")
        buffer = lines.pop()  # Letzte unvollständige Zeile behalten

        for resp in lines:
            if resp.startswith("PING"):
                sock.send("PONG\n".encode("utf-8"))
                continue

            if "PRIVMSG" in resp:
                try:
                    username = resp.split("!", 1)[0][1:]
                    message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1]
                    print(f"{username}: {message.strip()}")

                    if WATCHED_NAME.lower() in message.lower():
                        channel = resp.split("PRIVMSG")[1].split("#")[1].split(" ")[0]
                        alert = f"🔔 **{WATCHED_NAME}** wurde erwähnt in **#{channel}** von **{username}**:\n> {message.strip()}"
                        send_to_discord(alert)
                except Exception as e:
                    print("Parsing-Fehler:", e)
    except Exception as e:
        print("Fehler beim Empfang der Daten:", e)

        username = resp.split("!", 1)[0][1:]
        message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1]

        print(f"{username}: {message.strip()}")

        if WATCHED_NAME.lower() in message.lower():
            channel = resp.split("PRIVMSG")[1].split("#")[1].split(" ")[0]
            alert = f"🔔 **{WATCHED_NAME}** wurde erwähnt in **#{channel}** von **{username}**:\n> {message.strip()}"
            send_to_discord(alert)

