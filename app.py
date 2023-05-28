import asyncio
import json
import openai
import sys
import textwrap
from tqdm import tqdm
import time
# Import additional libraries
import requests
from PIL import Image
import io

openai.api_key = "<your_api_key>"

def token_cost_calculator_gpt3(tokens_used):
    TOKEN_PRICE_GPT3 = 0.002 / 1000  # $0.002 per 1K tokens
    return tokens_used * TOKEN_PRICE_GPT3

def token_cost_calculator_dalle():
    TOKEN_PRICE_DALLE = 0.016  # $0.016 per image
    return TOKEN_PRICE_DALLE

async def ask_gpt3(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    tokens_used = response["usage"]["total_tokens"]
    return response.choices[0].message["content"].strip(), tokens_used

async def read_input(prompt):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

def show_help():
    print("Help:")
    print("------")
    print("To interact with the game, simply type your actions or questions, such as 'go north', 'take the key', or 'what's in the room?'.")
    print("Type 'quit' or 'exit' to leave the game.")

async def generate_dalle_image(prompt, image_filename):
    # Add "in high definition" to the prompt
    hd_prompt = f"{prompt} in high definition"

    response = openai.Image.create(
        prompt=hd_prompt,
        n=1,
        size="256x256"
    )
    image_url = response["data"][0]["url"]

    # Download the image
    response = requests.get(image_url)

    # Open the image using PIL and save it as a jpg file
    image = Image.open(io.BytesIO(response.content))
    image.save(image_filename, "JPEG")

async def main():
    print("Welcome to the text adventure game!")
    print("------------------------------------")
    print("Type 'help' if you need assistance.")
    print("Type 'quit' or 'exit' to leave the game.")
    print("------------------------------------")

    in_game = True
    previous_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant in a text-based adventure game where the player wakes up in Central Park, New York. "
                "The player can do anything they want in this open-world game. Understand the player's input and provide detailed responses that help them progress in the game. "
                "When they ask for help, give them guidance on what they can do in the game. When they describe an action or ask a question, provide a response that helps them advance in the story."
            ),
        }
    ]

    total_gpt3_cost = 0
    total_dalle_cost = 0

    while in_game:
        question = await read_input("\nWhat do you want to do? ")

        if question.lower() == "help":
            show_help()
            continue

        previous_messages.append({"role": "user", "content": question})
        gpt_response, tokens_used = await ask_gpt3(previous_messages)
        previous_messages.append({"role": "assistant", "content": gpt_response})

        cost_gpt3 = token_cost_calculator_gpt3(tokens_used)
        total_gpt3_cost += cost_gpt3

        # Call DALL-E to generate an image related to the GPT-3 response
        image_filename = f"{len(previous_messages) - 1}_response_image.jpg"
        await generate_dalle_image(gpt_response, image_filename)

        cost_dalle = token_cost_calculator_dalle()
        total_dalle_cost += cost_dalle

        print("Game State:")
        print("-----------")
        print(textwrap.fill(gpt_response, width=70))
        print("------------------------------------")
        print("Type 'help' if you need assistance.")
        print("Type 'quit' or 'exit' to leave the game.")
        print("------------------------------------")

        print(f"Current message cost: GPT-3: ${cost_gpt3:.6f} | DALL-E: ${cost_dalle:.6f}")
        print(f"Total cost: GPT-3: ${total_gpt3_cost:.6f} | DALL-E: ${total_dalle_cost:.6f}")

if __name__ == "__main__":
    asyncio.run(main())
