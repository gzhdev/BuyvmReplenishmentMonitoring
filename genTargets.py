import asyncio
import lxml
import httpx
from bs4 import BeautifulSoup
import re
from pprint import pprint


# 变量
targets = {}


async def genTarget(gid):
    global targets
    STORE_URL = 'https://my.frantech.ca/cart.php'
    async with httpx.AsyncClient() as client:
        r = await client.get(STORE_URL, params={'gid': gid})
        soup = BeautifulSoup(r.text, 'lxml')
        packages = soup.find_all('div', attrs={'class': 'package'})
        for package in packages:
            link = package.find(id=re.compile('product')).attrs['href']
            pid = eval(link.split('&')[-1].split('=')[-1])
            # targets[pid] = [package.h3.string, 0]
            targets[pid] = {'name': package.h3.string, 'status': 0}
    return 0


def genTargets(gidList):
    global targets
    loop = asyncio.get_event_loop()
    tasks = [genTarget(gid) for gid in gidList]
    runtime = loop.run_until_complete(asyncio.wait(tasks))
    return targets


if __name__ == '__main__':
    gids = [39, 46]
    pprint(genTargets(gids))
