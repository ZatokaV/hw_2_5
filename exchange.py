import platform
from datetime import datetime, timedelta
import aiohttp
import asyncio
import sys

actual_currency = ['EUR', 'USD']


def arg_to_int() -> int:
    if len(sys.argv) == 1:
        return 1
    if len(sys.argv) == 2:
        count_days = int(sys.argv[-1])
        if 0 < count_days <= 10:
            return count_days
        raise ValueError('You can see only 10 last days')
    if len(sys.argv) == 3:
        new_currency = sys.argv[-1]
        actual_currency.append(new_currency)
        # print(actual_currency)
        count_days = int(sys.argv[-2])
        if 0 < count_days <= 10:
            return count_days
        raise ValueError('You can see only 10 last days')
    raise ValueError('Invalid args')


def arg_to_days(days=None) -> list[str]:
    today: datetime = datetime.today()

    if days:
        try:
            delta = int(days)
        except ValueError:
            delta = 1
    else:
        delta: int = arg_to_int()

    if delta > 1:
        first_day = today - timedelta(delta)
        list_days: list = []
        while first_day < today:
            first_day += timedelta(1)
            list_days.append(first_day.strftime('%d.%m.%Y'))
        return list_days
    return [today.strftime('%d.%m.%Y')]


def generate_api(days=None) -> list[str]:
    all_days = []
    for day in arg_to_days(days):
        API = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day}'
        all_days.append(API)
    return all_days


async def exchange(days=None) -> list[dict]:
    output = []
    for url in generate_api(days):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                date: str = result['date']
                day_rate = {}
                for el in result['exchangeRate']:
                    if el['currency'] in actual_currency:
                        day_rate[el['currency']] = {'sale': el['saleRate'], 'purchase': el['purchaseRate']}
                one_day_date = {date: day_rate}
                output.append(one_day_date)
    return output


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(exchange())
    print(r)
