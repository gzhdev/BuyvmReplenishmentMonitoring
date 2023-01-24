import httpx
import logging
from logging import handlers
import time
import os
import asyncio
from genTargets import genTargets

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
logger.setLevel(logging.INFO)

# 常量
URL = 'https://my.frantech.ca/cart.php'

# 全局变量
# 监控的项目，由{pid:{name:status}}构成
gids = [39, 46]
targets = genTargets(gids)
logger.info(f"Gen targets successfully. The targets number is {len(targets)}")


async def sendMsg(msg):
    MSG_URL = r''  # Wecomchan通知推送URL，可以参考https://github.com/easychen/wecomchan搭建
    params = {
        'sendkey': '',  # Wecomchan的sendkey
        'text': msg
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(MSG_URL, params=params)
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
        logger.info("Sleep 300s.")
        time.sleep(300)
