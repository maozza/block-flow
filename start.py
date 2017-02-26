from start_class import TaskerDo
import signal


def handler(signum,frame):
    raise KeyboardInterrupt("Recive kill signal %s"%(signum,))




class TaskDoFile(TaskerDo):
    def get_ips_from_file(self,file):
        try:
            with open(file) as f:
                for line in f:
                    self.ip_list.append(line.rstrip())
        except FileNotFoundError:
            pass



if __name__ == '__main__':
    '''
    examples:
    '''

    i = TaskDoFile('config/configuration.yml')
    #i.ip_list = ['216.239.32.10', '216.239.34.10', '216.239.36.10', '216.239.38.10']
    '''
    Add any job here
    '''
    schedule=dict(name="get ip from file", trigger='interval', params = dict(seconds=20))
    i.set_scheduler(job=i.get_ips_from_file,args=('/var/tmp/ip.lst',),schedule=schedule)
    signal.signal(signal.SIGTERM,handler)
    try:
        i.stat()
    except KeyboardInterrupt:
        i.stop()



