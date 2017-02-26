from start_class import TaskerDo
import signal


def handler(signum,frame):
    raise KeyboardInterrupt("Recive kill signal %s"%(signum,))


def get_ips_from_file():
    file = '/home/mozzi/test.list'
    ip_list = []
    try:
        with open(file) as f:
            for line in f:
                ip_list.append(line.rstrip())
    except FileNotFoundError:
        pass
    return ip_list


if __name__ == '__main__':
    '''
    examples:
    '''

    i = TaskerDo('config/configuration.yml')
    i.ip_list = get_ips_from_file()
    #i.ip_list = ['216.239.32.10', '216.239.34.10', '216.239.36.10', '216.239.38.10']
    '''
    Add any job here
    '''
    schedule=dict(name="get ip from file", trigger='interval', params = dict(seconds=10))
    i.set_scheduler(job=get_ips_from_file,schedule=schedule)
    signal.signal(signal.SIGTERM,handler)
    try:
        i.stat()
    except KeyboardInterrupt:
        i.stop()



