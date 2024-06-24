import os
import json
from dotenv import load_dotenv
from discord import Intents, Client, Message
from difflib import get_close_matches

# Load token from environment
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define the command prefix
COMMAND_PREFIX = "?"

# Set up bot
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# Flag to control bot operation
bot_running = True

# AI functions
def load_knowledge(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"questions": []}

def save_knowledge(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_input: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_input, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge: dict) -> str | None:
    for q in knowledge["questions"]:
        if q["question"].lower() == question.lower():
            return q["answer"]
    return None

async def get_response(user_message: str) -> str:
    knowledge = load_knowledge('knowledge.json')
    best_match = find_best_match(user_message, [q["question"] for q in knowledge["questions"]])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge)
        return answer
    else:
        return "Faust doesn't know this yet. Can you teach me?"

async def collect_new_answer(message: Message, user_message: str) -> None:
    def check(m):
        return m.author == message.author and m.channel == message.channel

    await message.channel.send("Please type the answer or 'skip' to skip:")
    answer_message = await client.wait_for('message', check=check)
    new_answer = answer_message.content

    if new_answer.lower() != 'skip':
        knowledge = load_knowledge('knowledge.json')
        knowledge["questions"].append({"question": user_message, "answer": new_answer})
        save_knowledge('knowledge.json', knowledge)
        await message.channel.send('Thank you for your information')

async def send_message(message: Message, user_message: str) -> None:
    global bot_running

    if not user_message:
        print('(unba bunga)')
        return

    if user_message.strip().lower() == "stop":
        bot_running = False
        await message.channel.send("Bot is stopping.")
        await client.close()
        return

    is_private = user_message.startswith(COMMAND_PREFIX)
    user_message = user_message[len(COMMAND_PREFIX):] if is_private else user_message

    try:
        response = await get_response(user_message)
        await message.channel.send(response)
        
        if response == "Faust doesn't know this yet. Can you teach me?":
            await collect_new_answer(message, user_message)
    except Exception as e:
        print(f"Error handling message: {e}")

# Start-up bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# Incoming message
@client.event
async def on_message(message: Message) -> None:
    global bot_running

    if message.author == client.user or not bot_running:
        return

    if message.content.startswith(COMMAND_PREFIX):
        username = str(message.author)
        user_message = message.content
        channel = str(message.channel)

        print(f'[{channel}] {username}: "{user_message}"')
        
        # Handle the user's query after the initial response
        await send_message(message, user_message)

# Main entry point
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
