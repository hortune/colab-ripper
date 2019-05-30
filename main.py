import requests
import json
import socketio
import random
import ipdb

class Socketio_agent:
    sio = socketio.Client()
    def __init__(self, endpoint, headers, cookies):
        self.url = "https://colab.research.google.com/?authuser=0"
        self.headers = headers
        self.headers.update({ "cookie": "; ".join("{}={}".format(x,y) 
                        for x,y in cookies.items())
                                    })
        self.endpoint = endpoint
    
    def connect(self):
        self.sio.connect(url = self.url, 
                         headers = self.headers, 
                         transports = "polling",
                         socketio_path='tun/m/{}/socket.io'.format(self.endpoint))
        self.sio.wait()

    @sio.on('connect')
    def on_connect():
        print('I\'m fucking connected')
        

class colab_connector:
    '''
    TODO
    - Create session
    '''
    def __init__(self,cookies,headers,nbid):
        self.c = requests.Session() 
        self.c.headers.update(headers) 
        self.c.cookies.update(cookies)
        self.endpoint = self.get_endpoint()
        self.base_addr = "https://colab.research.google.com/tun/m/{}".format(self.endpoint)
        self.session = self.get_session()
        self.kernelspec = self.get_kernelspecs()
        self.nbid = nbid # The file id in google drive
        self.send_session()
        self.agent = Socketio_agent(
                        endpoint = self.endpoint, 
                        headers = self.c.headers,
                        cookies = self.c.cookies) 
    def get_endpoint(self):
        res = self.c.get("https://colab.research.google.com/tun/m/assign", params={"authuser":0})
        endpoint = json.loads(res.text[res.text.index('\n')+1:].strip())['endpoint']
        return endpoint
    
    def get_session(self):
        url = "{}/api/sessions".format(self.base_addr)
        s_info = json.loads(self.c.get(url, params={"authuser":0}).text)
        return s_info

    def get_kernelspecs(self):
        url = "{}/api/kernelspecs".format(self.base_addr)
        k_info = json.loads(self.c.get(url, params={"authuser":0}).text)
        return k_info

    def send_session(self):
        url = "{}/api/sessions".format(self.base_addr)
        data =  {
                    "name":"Untitled2.ipynb",
                    "path":"fileId={}".format("1zUe2STXk6TevV0_1xpkyUD3GbF9830sp"),
                    "type":"notebook",
                    "kernel":{
                        "name":"python3"
                    }
                }
        res = self.c.post(url, params={"authuser":0}, json=data)
        print(res.status_code)
        assert res.status_code // 100 == 2
    
    def start(self):
        self.agent.connect()

if __name__ == '__main__':
    cookies = json.load(open("secret/cookie.json"))
    headers = {
                 "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                 "x-colab-tunnel": "Google",
                 "referer": "https://colab.research.google.com/",
                 "accept-encoding": "gzip, deflate, br",
                 "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
                 "accept": "*/*",
                 "authority": "colab.research.google.com",
            }
    colab = colab_connector(cookies=cookies,
                            headers=headers,
                            nbid="1zUe2STXk6TevV0_1xpkyUD3GbF9830sp")
    
    colab.start()
    """
    #colab.start()
    print(colab.endpoint)
    print(json.dumps(colab.get_session(), indent=2))
    print(json.dumps(colab.kernelspec, indent=2))
    #colab.send_session()
    #print(json.dumps(colab.get_session(),indent=2))
    #print(json.dumps(colab.get_kernelspecs(),indent=2))
    """
