def validate_token(token: str):
    valid_tokens = {
                    "meu_token": "usuario1", 
                    "meu_token_plugin2": "plugin2",
                    }
    return token in valid_tokens