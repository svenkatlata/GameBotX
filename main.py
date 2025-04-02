import discord
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5
MAX_TOKENS = 250

openai_client = OpenAI(api_key=OPENAI_API_KEY)

with open("GameBotX.txt", "r") as f:
    SYSTEM_MESSAGE = f.read().strip()

allowed_mentions = discord.AllowedMentions(users=True, roles=False, everyone=False)

messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

class MyClient(discord.Client):

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        
        channel = self.get_channel(CHANNEL_ID)

        if channel:
            print(f"Found channel: {channel.name} (ID: {channel.id})")
            try:
                await channel.send("Hello everyone! I'm online and ready to assist. Mention me to chat! \\U0001F60A ")
                print("Message sent successfully!")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("Error: Could not find the channel. Make sure CHANNEL_ID is correct and the bot has access.")

    async def on_message(self, message):
        # Don't respond to itself
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            # Remove bot mention from the message content
            user_message = message.content.replace(f'<@{self.user.id}>', '').strip()
            user_id = message.author.id

            try:
                messages.append({"role": "user", "user_id": user_id, "content": user_message})
                
                response = openai_client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )

                assistant_message = response.choices[0].message.content.strip()
                messages.append({"role": "assistant", "content": assistant_message})
                await message.channel.send(f"{message.author.mention} {assistant_message}", allowed_mentions=allowed_mentions)

            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("Oops! Something went wrong. Try again later.", allowed_mentions=allowed_mentions)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
