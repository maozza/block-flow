import redis
from jinja2 import Template
import os
from _datetime import datetime

redis_host = "localhost"
client = redis.Redis(host=redis_host)


def create_conf(template_file,**kwargs):
    with open(template_file) as t:
        template_str = t.read()
    t=Template(template_str)
    return t.render(**kwargs)

def redis_push_ip_list(ip_list,expiration):
    for key in ip_list:
        _ = client.set(key,None,ex=expiration)
    return  True

def redis_get_ips_list():
    ips = client.keys('*')
    return [i.decode() for i in ips]

def write_conf(conf,location,backup=True):
    if backup and os.path.exists(location):
        date = datetime.now().strftime('%y%m%d%H%M%S')
        os.rename(location,location +'.'+ date)
    with open(location,'w') as conf_file:
        _ = conf_file.write(conf)

class CommanFail(Exception):
    pass

def reload_service(commands_list):
    for command in commands_list:
        exit_status = os.system(command)
        if exit_status > 0:
            raise CommanFail("Command %s failed with status %s"%(command,exit_status))
    return True




