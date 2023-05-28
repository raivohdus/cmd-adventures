# Import the OpenAI library
import openai
import os

# Replace "your_api_key" with your actual OpenAI API key
openai.api_key = "your_api_key"


# Add the token and cost calculator
def calculate_cost(tokens):
    cost_per_k_tokens = 0.03 if tokens <= 8000 else 0.06
    return round(tokens * cost_per_k_tokens / 1000, 4)

def calculate_tokens(text):
    return openai.Completion.tokens(text)

# First, let's create a function to read questions from a text file:

def read_questions_from_file(filename):
    with open(filename, "r") as file:
        questions = file.readlines()
    return [question.strip() for question in questions]

# Calculate tokens and cost
tokens = calculate_tokens(content)
cost = calculate_cost(tokens)

def ask_gpt_3(question, num_answers=1):
    response = openai.ChatCompletion.create(
        model="gpt-3",
        messages=[
            {"role": "system", "content": "Create different game.js files with filenames such as game_1_1.js, game_1_2.js, game_1_3.js, game_2_1.js, and so on. Try different ways to create the most interactive experience you can, for a player to simply be asked questions after he starts the game.py file in PowerShell. The game's point is to provide an interactive prompt to the player, and when he answers, an image should pop up describing the following situation and the next prompt. The Description to Dall-E should be first written by you to make the most accurate description as possible, and then sent to Dall-E. An original game.py file is also in the input." + content},
            {"role": "user", "content": question},
        ],
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        n=num_answers,
    )

    answers = [choice.message['content'].strip() for choice in response.choices]

    return answers

# ... (rest of the code is the same as before) ...

#modify the code to read questions from the "question.txt" file and save the generated code files with different names:
if __name__ == "__main__":
    questions = read_questions_from_file("question.txt")
    
    for question_index, question in enumerate(questions):
        # Generate multiple answers for each question
        answers = ask_gpt_3(question, num_answers=3)

        for answer_index, answer in enumerate(answers):
            output_filename = f"game_{question_index + 1}_{answer_index + 1}.js"
            with open(output_filename, "w") as file:
                file.write(answer)
