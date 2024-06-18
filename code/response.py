from random import choice,randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    
    if lowered == 'nep':
        return 'The gay one ?'
    if lowered == ':noinho:':
        return 'Emoji này gợi nhớ mị lúc Nep gay thật...giờ vẫn thế' 
    if lowered == 'soi': 
        return ':fire:'
    if lowered == 'hmm gay':
        return ':gay'

