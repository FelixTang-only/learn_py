# 使用模块'
import sys;
sys.path.append("/Users/apple/Work/learn_py")
import test1
print(test1.test())
# print(test.a)
# 安装第三方模块
# requests
import requests
r = requests.get('https://www.baidu.com')
print(r.status_code)
# r.text

