from start_class import TaskerDo
from elasticsearch_query_class import elQuery
import signal


'''
this is an example file, it gives a basic understanding on how to use the tool
'''

# handle kill signal
def handler(signum,frame):
    raise KeyboardInterrupt("Recive kill signal %s"%(signum,))




class TaskrDoExample(TaskerDo):
    '''
    Add any job here, can be more than one
    '''
    def get_ips_from_file(self,file):
        '''
        example for reciveing the ip list from file
        :param file: file path
        :return:
        '''
        try:
            with open(file) as f:
                for line in f:
                    self.ip_list.append(line.rstrip())
        except FileNotFoundError:
            pass
    def get_ips_from_elasticsearch(self,obj):
        '''
        example for reciveing the ip list from Elasticsearch
        :param obj: elasticsearch_query_class object
        :return:
        '''
        self.ip_list += obj.query()






if __name__ == '__main__':
    # instantiate the  extended TaskerDo class
    i = TaskrDoExample('config/configuration_sample.yml')

    # set schedule for the Elasticsearch query job and start it up
    elastic_q = elQuery('config/elasticsearch_query_sample.yml')
    schedule = dict(name="block post to my app", trigger='interval', params=dict(seconds=60))
    i.set_scheduler(job=i.get_ips_from_elasticsearch,args=(elastic_q,),schedule=schedule)

    # Example: set schedule for the file fetch job and start it up
    # schedule=dict(name="get ip from file", trigger='interval', params = dict(seconds=20))
    # i.set_scheduler(job=i.get_ips_from_file,args=('/var/tmp/ip.lst',),schedule=schedule)

    # Example: set schedule for the Elasticsearch query job and start it up
    #elastic_q2 = elQuery('config/elasticsearch_query_sample2.yml')
    # schedule = dict(name="get ip from Elasticsearch", trigger='interval', params=dict(seconds=60))
    # i.set_scheduler(job=i.get_ips_from_elasticsearch,args=(elastic_q2,),schedule=schedule)


    signal.signal(signal.SIGTERM,handler)

    try:
        # running the scheduler
        i.start()
    except KeyboardInterrupt:
        # stop on interrupt
        i.stop()



