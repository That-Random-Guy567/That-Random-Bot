from random import choice, randint

def get_response(user_input:str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return "Well, you're awfully silent..."
    elif 'hello' is lowered:
        return "Hello there!"
    elif 'how are you' in lowered:
        return "I'm good thanks!"
    elif 'bye' in lowered:
        return "See ya later!"
    elif 'roll dice' in lowered:
        return f"You rolled {randint(1,6)}"

    else:
        return choice(['I do not understand',
                       'What are you talking about?',
                       'Do you mind rephrasing that?',
                       'I\'m a helicopter! (easter egg!)'])