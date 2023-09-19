import platform
from datetime import datetime, timedelta
import logging
import aiohttp
import asyncio
import sys


async def request(url: str):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def get_exchange(date, curr):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    result = await request(url)
    if result:
        try:
            (exc,) = list(
                filter(lambda el: el["currency"] == "USD", result["exchangeRate"])
            )
            (emp,) = list(
                filter(lambda el: el["currency"] == "EUR", result["exchangeRate"])
            )
            (adc,) = list(
                filter(lambda el: el["currency"] == curr, result["exchangeRate"])
            )
            usd = f"USD: buy: {exc['purchaseRate']}, sale: {exc['saleRate']}. Date: {date}"
            eur = f"EUR: buy: {emp['purchaseRate']}, sale: {emp['saleRate']}. Date: {date}"
            adcurr = f"{curr}: buy: {adc['purchaseRate']}, sale: {adc['saleRate']}. Date: {date}"
            return usd, eur, adcurr
        except KeyError:
            return "Failed to retrieve data. Data format is invalid."
    return "Failed to retrieve data"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <days> <currency>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Error: <days> must be an integer.")
        sys.exit(1)

    try:
        curr = str(sys.argv[2])
    except ValueError:
        print("Error: <currency> must be a string.")
        sys.exit(1)

    if days > 10:
        print("Error: The maximum number of days is 10.")
        sys.exit(1)

    if len(curr) != 3:
        print("Error: The currency param should be 3 letters long")

    today = datetime.now()
    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%d.%m.%Y")
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(get_exchange(date, curr))
        print(result)
