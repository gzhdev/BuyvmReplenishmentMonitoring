import httpx
import logging
from logging import handlers
import time
import os
import asyncio

# 日志
if not os.path.exists("./logs"):
    os.makedirs("./logs")

logger = logging.getLogger()
logging.basicConfig(
    encoding='utf-8',
)
handler = logging.StreamHandler()
th = handlers.TimedRotatingFileHandler(
    filename="logs/debug.log",
    when='D',
    backupCount=30,
    encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s\t')
handler.setFormatter(formatter)
th.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(th)
logger.setLevel(logging.DEBUG)

# 常量
targets = {
    1423: {'name': 'LU RYZEN KVM 1GB', 'status': 0},
    1424: {'name': 'LU RYZEN KVM 2GB', 'status': 0},
    1425: {'name': 'LU RYZEN KVM 4GB', 'status': 0},
    1426: {'name': 'LU RYZEN KVM 8GB', 'status': 0},
    1427: {'name': 'LU RYZEN KVM 12GB', 'status': 0},
    1428: {'name': 'LU RYZEN KVM 16GB', 'status': 0},
    1429: {'name': 'LU RYZEN KVM 20GB', 'status': 0},
    1430: {'name': 'LU RYZEN KVM 24GB', 'status': 0},
    1431: {'name': 'LU RYZEN KVM 28GB', 'status': 0},
    1432: {'name': 'LU RYZEN KVM 32GB', 'status': 0},
    1486: {'name': 'LU Block Storage Slab - 256GB', 'status': 0},
    1487: {'name': 'LU Block Storage Slab - 512GB', 'status': 0},
    1488: {'name': 'LU Block Storage Slab - 1TB', 'status': 0},
    1489: {'name': 'LU Block Storage Slab - 2TB', 'status': 0},
    1490: {'name': 'LU Block Storage Slab - 3TB', 'status': 0},
    1491: {'name': 'LU Block Storage Slab - 4TB', 'status': 0},
    1492: {'name': 'LU Block Storage Slab - 5TB', 'status': 0},
    1493: {'name': 'LU Block Storage Slab - 6TB', 'status': 0},
    1494: {'name': 'LU Block Storage Slab - 7TB', 'status': 0},
    1495: {'name': 'LU Block Storage Slab - 8TB', 'status': 0},
    1496: {'name': 'LU Block Storage Slab - 9TB', 'status': 0},
    1497: {'name': 'LU Block Storage Slab - 10TB', 'status': 0}
}
URL = 'https://my.frantech.ca/cart.php'


async def sendMsg(msg):
    msg_url = r'http://wecom.devsp.eu.org'
    params = {
        'sendkey': 'WCMnYiCUapzHLU2zFPmq9hoxLqkFi574gf6',
        'text': msg
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(msg_url, params=params)
        logger.info(f"sendMsg, status_code={r.status_code}")
    return r.status_code


async def getStatusCode(pid):
    logger.debug(f"Check {pid}")
    global URL, targets
    params = {
        'a': 'add',
        'pid': pid
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(URL, params=params)
    logger.debug(f"{pid} status_code={r.status_code} status={targets[pid]['status']}")
    if r.status_code == 302 and targets[pid]['status'] == 0:
        targets[pid]['status'] = 1
        logger.debug(f"change {pid} status to 1")
        msg = rf"{targets[pid]['name']}补货了，<a href='{URL}?a=add&pid={pid}'>点击购买</a>"
        logger.debug(msg)
        await sendMsg(msg)
        logger.info(f"{pid} is replenishment, send message to user.")
    elif r.status_code == 200 and targets[pid]['status'] == 1:
        logger.info(f"{pid} is Out of Stock")
        targets[pid]['status'] = 0
    return 0


def main():
    loop = asyncio.get_event_loop()
    tasks = [getStatusCode(pid) for pid in targets.keys()]
    runtime = loop.run_until_complete(asyncio.wait(tasks))
    # runtime.close()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)
