import os
import json
TOKEN = os.getenv('TOKEN', default='bot token you got from BotFather')  # Set default if you do not plan to use ENVs
LIST_OF_ADMINS = json.loads(os.getenv('LIST_OF_ADMINS', default='["numericalid1", "numericalid2"]'))
