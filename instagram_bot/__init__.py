from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay

from instagram_bot.InstagramBot import InstagramBot
from hidden.insta.access_code import access_code
from hidden.insta.app_data import app_data

insta = InstagramBasicDisplay(**app_data)
insta_bot = InstagramBot(insta, access_code)
