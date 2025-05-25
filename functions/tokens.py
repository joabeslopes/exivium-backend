async def get_token_info(token: str):
    tokens = {
        "meu_token": {  
            "name": "usuario1",
            "role": "user"
        },
        "meu_token_exemplo": { 
            "name": "exemplo",
            "role": "plugin"
        }
    }
    if token in tokens:
        return tokens[token]
    else:
        return False