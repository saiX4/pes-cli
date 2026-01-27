import inquirer

# 1. Define the Questions
questions = [
    # A list where you pick ONE option (Arrow Keys)
    inquirer.List('course',
        message="Which course are you studying?",
        choices=['Python', 'Mechanics', 'Maths'],
    ),
    
    # A checkbox where you pick MULTIPLE options (Spacebar)
    inquirer.Checkbox('tools',
        message="What tools do you need?",
        choices=['Notebook', 'Calculator', 'Laptop'],
    ),
]

# 2. Run the Prompt (This pauses the script)
# The library takes control of the screen here.
answers = inquirer.prompt(questions)

# 3. Use the Answers
# It returns a simple dictionary: {'course': 'Python', 'tools': ['Laptop']}
print(f"You chose {answers['course']}")