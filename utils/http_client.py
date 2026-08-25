import requests

# 统一禁用代理配置
NO_PROXY = {"http": None, "https": None}

def send_request(method, url, **kwargs):
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("proxies", NO_PROXY)
    return requests.request(method, url, **kwargs)
