from decouple import config


class Settings:
    pass


settings = Settings()

settings.DEBUG = config('DEBUG', default=True, cast=bool)
settings.BLINKTRADE_API_KEY = config('BLINKTRADE_API_KEY')
settings.BLINKTRADE_API_SECRET = config('BLINKTRADE_API_SECRET')
if settings.DEBUG:
    settings.BLINKTRADE_API_URL = 'https://api.testnet.blinktrade.com'
else:
    settings.BLINKTRADE_API_URL = 'https://api.blinktrade.com'
settings.BLINKTRADE_API_VERSION = 'v1'
settings.CURRENCY = 'BRL'
# 4 is foxbit
settings.BROKER = '4'
# Don't change this or you will mess up every
settings.PRECISION = 100000000
# In cents
settings.MAX_ACCEPTABLE_PRICE_IN_CENTS = config('MAX_ACCEPTABLE_PRICE_IN_REAL', cast=int) * 100
settings.PER_ORDER_IN_CENTS = config('PER_ORDER_IN_REAL', cast=int) * 100
