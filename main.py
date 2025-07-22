import socket
import requests
import os
import time

TWITCH_NICK = os.getenv("TWITCH_NICK")
TWITCH_CHANNELS = os.getenv("TWITCH_CHANNELS", "").split(",")
WATCHED_NAME = os.getenv("WATCHED_NAME")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def connect_to_twitch():
    sock = socket.socket()
    sock.connect(("irc.chat.twitch.tv", 6667))
    sock.send(f"PASS oauth:schrott\n".encode("utf-8"))  # kein Login nötig
    sock.send(f"NICK {TWITCH_NICK}\n".encode("utf-8"))
    for channel in TWITCH_CHANNELS:
        sock.send(f"JOIN #{channel.strip()}\n".encode("utf-8"))
    print("✅ Bot verbunden und hört zu...")
    return sock

while True:
    try:
        sock = connect_to_twitch()
        while True:
            resp = sock.recv(2048).decode("utf-8")

            if resp.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\n".encode("utf-8"))
                continue

            if "PRIVMSG" in resp:
                try:
                    username = resp.split("!")[0][1:]
                    channel = resp.split("PRIVMSG #")[1].split(" :")[0].strip()
                    message = resp.split("PRIVMSG", 1)[1].split(":", 1)[1]

                    if WATCHED_NAME.lower() in message.lower():
                        print(f"👀 {username} erwähnte {WATCHED_NAME} in {channel}: {message.strip()}")
                        requests.post(DISCORD_WEBHOOK_URL, json={
                            "content": (
                                f"👀 **{username}** erwähnte `{WATCHED_NAME}` im Chat von **{channel}**\n"
                                f"💬 *\"{message.strip()}\"*\n"
                                f"🔗 https://twitch.tv/{channel}"
                            )
                        })
                except Exception as e:
                    print(f"⚠️ Fehler beim Verarbeiten der Nachricht: {e}")
    except Exception as e:
        print(f"🔁 Verbindung verloren ({e}). Neuer Versuch in 10 Sekunden...")
        time.sleep(10)
