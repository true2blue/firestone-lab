import requests
import configparser
import logging

class ProxyManager(object):
    
    _logger = logging.getLogger(__name__)
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(f'./config/api.ini', encoding='utf-8')
        self.refresh_tunnel()
            
    def refresh_tunnel(self):
        response = requests.get(f'https://share.proxy.qg.net/pool?key={self.config["proxy"]["key"]}&num={self.config["proxy"]["num"]}&area=&isp=0&format=json&distinct=true')
        result = response.json()
        if result['code'] == 'SUCCESS' and len(result['data']) > 0:
            self.tunnel = {
                'auth' : {
                    'key' : self.config["proxy"]["key"],
                    'pwd' : self.config["proxy"]["pwd"]
                }
            }
            self.tunnel.update(result['data'][0])
        else:
            self.tunnel = None
            ProxyManager._logger.error(f'failed to get proxy ips, {result}')
            
    def get_tunnel(self):
        return self.tunnel