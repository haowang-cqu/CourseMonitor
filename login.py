import requests
from bs4 import BeautifulSoup
from encrypt import *
from typing import Dict
from urllib import parse


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}


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


def login(username: str, password: str) -> requests.Session:
    """用户登录
    """
    session = requests.Session()

    # step1: 获取登录页面
    login_page_url = "http://authserver.cqu.edu.cn/authserver/login"
    resp = session.get(
        url=login_page_url,
        params={
            "service": "http://my.cqu.edu.cn/authserver/authentication/cas"
        },
        headers=headers,
        allow_redirects=False
    )
    if resp.status_code != 200:
        return None
    
    # step2: 构造登录表单并提交
    login_formdata = get_formdata(resp.text, username, password)
    resp = session.post(
        url=login_page_url,
        headers=headers,
        data=login_formdata,
        allow_redirects=False
    )
    if resp.status_code != 302:
        return None

    # step3: 重定向到目标服务
    target_url = resp.headers["Location"]
    resp = session.get(
        url=target_url,
        headers=headers,
        allow_redirects=False
    )
    if resp.status_code != 302:
        return None
    
    # step4: 获取oauth token
    oauth_url = "http://my.cqu.edu.cn/authserver/oauth/authorize"
    resp = session.get(
        url=oauth_url,
        params={
            "client_id": "enroll-prod",
            "response_type": "code",
            "scope": "all",
            "state": "",
            "redirect_uri": "http://my.cqu.edu.cn/enroll/token-index"
        },
        headers=headers, 
        allow_redirects=False
    )
    if resp.status_code != 302:
        return None
    
    # step5: 生成oauth验证表单并提交验证
    # 从Location中取出code
    params = parse.parse_qs(parse.urlparse(resp.headers["Location"]).query)
    oauth_formdata = {
        "client_id": "enroll-prod",
        "client_secret": "app-a-1234",
        "code": params["code"][0],
        "redirect_uri": "http://my.cqu.edu.cn/enroll/token-index",
        "grant_type": "authorization_code"
    }
    # 加入Basic验证, 值为client_secret的base64编码, 这里写死
    headers["Authorization"] = "Basic ZW5yb2xsLXByb2Q6YXBwLWEtMTIzNA=="
    oauth_url = "http://my.cqu.edu.cn/authserver/oauth/token"
    resp = session.post(
        url=oauth_url,
        headers=headers,
        data=oauth_formdata
    )
    if resp.status_code != 200:
        return None
    headers["Authorization"] = "Bearer " + resp.json()["access_token"]
    
    return session