from core.bot import logger

def get_bot_config():
    # Import here to avoid circular import
    from constants import WHICH_BOT
    
    config = {
        'emojis': {},
        'token_name': ''
    }
    
    if WHICH_BOT:
        logger.info("Running as THAT RANDOM BOT")
        config['emojis'] = {
            "PEPE_YES": "<:pepe_yes:1381571891265011772>",
            "PEPE_NO": "<:pepe_no:1381571865063194727>",
            "BOT_PFP": "<:bot_pfp:1381571919958249562>",
        }
        config['token_name'] = "DISCORD_TOKEN"
    else:
        logger.info("Running as ZE RANDOM TEST BOT")
        config['emojis'] = {
            "PEPE_YES": "<:pepe_yes:1385176461023117383>",
            "PEPE_NO": "<:pepe_no:1385176421848322048>",
        }
        config['token_name'] = "DISCORD_TOKEN_test"
    
    return config