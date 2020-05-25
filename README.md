cwtgbot

To run your own instance, clone this repo. Get an API key from the @BotFather.

`virtualenv -p python3.8 venv`
`. venv/bin/activate`
`pip install -r requirements.txt`

Create `secrets.py` based on `secrets.py.example`. Put in the API key and change to your own TG-id for admin.

run `python bot.py`
in another terminal run `python publicapi.py` to have current price data available

See BotFather.txt for some tips on making the bot look good.
