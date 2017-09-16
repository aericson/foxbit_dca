# Foxbit DCA

## ATENTION: This is your money, take a look at the code before using it.

Dollar-cost averaging (DCA) is an investment technique of buying a fixed dollar amount of a particular investment on a regular schedule, regardless of the share price. The investor purchases more shares when prices are low and fewer shares when prices are high.
http://www.investopedia.com/terms/d/dollarcostaveraging.asp

This script aims to help you applying it to buy BTC using the Brazilian exchange Foxbit.

## Installation

1. Clone the repo
1. Create a virtualenv and activate it.
1. `pip install pipenv`
1. `pipenv install`
1. Create a `.env` file: `cp .env.example .env`
1. Edit `.env` following the Doc section bellow.

## Doc

`.env` variables:
- DEBUG: `True` to use the test blinktrade testnet or `False` to use production.
- BLINKTRADE_API_KEY: Your API key from foxbit website.
- BLINKTRADE_API_SECRET: Your API secret from foxbit webiste
- PER_ORDER_IN_REAL: the amount in real each order will be
- MAX_ACCEPTABLE_PRICE_IN_REAL: the maximum ammount you are willing to pay per BTC.

## Usage

1. Make sure you created `.env` file following Doc section above.
1. The script uses the follow algorithm:
    1. Delete pending orders it created on previous runs that didn't complete.
    1. Get the second highest price that someone used in a buy order.
    1. Use the second highest price to place a order with volume as defined in PER_ORDER_IN_REAL
    1. Exit

This script just run once, to use DCA you need to either run it manually in the interval you desire or schedule it with cron or another job scheduler.
