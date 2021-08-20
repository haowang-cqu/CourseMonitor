from requests import Session
import requests
from bs4 import BeautifulSoup
from .encrypt import *
from typing import Dict

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}
url = "http://authserver.cqu.edu.cn/authserver/login"


def get_formdata(html: str, username: str, password: str) -> Dict:
    """生成登录表单
    """
    soup = BeautifulSoup(html, 'html.parser')
    lt = soup.find("input", {"name": "lt"})['value']
    dllt = soup.find("input", {"name": "dllt"})['value']
    execution = soup.find("input", {"name": "execution"})['value']
    _eventId = soup.find("input", {"name": "_eventId"})['value']
    rmShown = soup.find("input", {"name": "rmShown"})['value']
    default = soup.find("script", {"type": "text/javascript"}).string
    key = default[57:-3]  # 获取盐，被用来加密
    iv = randomWord(16)
    # 参数使用Encrypt加密
    a = Encrypt(key=key, iv=iv)
    passwordEncrypt = a.aes_encrypt(randomWord(64)+str(password))
    # 传入数据进行统一认证登录
    return {
        'username': str(username),
        'password': passwordEncrypt,
        'lt': lt,
        'dllt': dllt,
        'execution': execution,
        '_eventId': _eventId,
        'rmShown': rmShown
    }


def login(username: str, password: str, service: str) -> Session:
    """单点登录
    """
    session = requests.session()
    # 请求单点登录页面
    login_page = session.get(
        url=url,
        params={
            "service": service
        },
        headers=headers,
        timeout=10)
    # 登录
    formdata = get_formdata(login_page.text, username, password)
    login_response = session.post(url=url, data=formdata, headers=headers, allow_redirects=False)
    # 重定向到目标服务
    session.get(url=login_response.headers['Location'], headers=headers, allow_redirects=False)
    return session
