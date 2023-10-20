import logging
import platform
from datetime import datetime, date
import asyncio
import argparse

import aiohttp

parser = argparse.ArgumentParser(description='App get exchange rate NBU')
parser.add_argument('-d', '--days', default=1, help="How much days")
parser.add_argument('-add', '--add_currency', default=None)
args = vars(parser.parse_args())  # object -> dict
days = args.get('days')
user_currency = args.get('add_currency')


def create_urls(value: int) -> list:
    url_prefix = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    current_datetime = datetime.today().date()
    users_input = int(value)
    if users_input > 10:
        users_input = 10
    urls = []
    for i in range(users_input):
        new_date = date(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day - i)
        urls.append(url_prefix + new_date.strftime("%d.%m.%Y"))
    return urls[::-1]


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f"Error status {response.status} for {url}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Connection error {url}: {e}")
            return None


def output(all_currencies, user_currency=None):
    default_currencies = ["USD", "EUR"]
    answer = ""
    if user_currency:
        default_currencies.append(user_currency)
    for item in all_currencies:
        answer += item['date'] + '\n'
        for currencies in item['exchangeRate']:
            if currencies['currency'] in default_currencies:
                answer += f"\t\t{currencies.get('currency')} buy : {currencies.get('saleRate')} sale: {currencies.get('purchaseRate')}\n"
    return answer


async def exchanger_run(days=1, user_currency=None):
    urls = create_urls(days)
    r = []
    for url in urls:
        r.append(request(url))
    result = await asyncio.gather(*r)
    return output(result, user_currency)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    res = asyncio.run(exchanger_run(days, user_currency))
    print(res)
