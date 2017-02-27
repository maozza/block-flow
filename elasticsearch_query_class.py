from elasticsearch import Elasticsearch
import yaml
from jinja2 import Template
import time
import json
import datetime

class elasticsearch_query:
    def __init__(self, query_file):
        self.get_configuration(query_file)
        self.get_time_range(self.config['minutes_until_now'])
        q = json.dumps(self.config['query_body'])
        query_body= self.render_j2(q, **self.range)
        self.es = Elasticsearch(hosts=self.config['host'])
        self.set_index()
        self.query(query_body,int(self.config['limit']))
    def get_configuration(self, conf_file):
        '''
        :param conf_file: yaml configuration file with report data
        :return: configuration data
        '''
        with open(conf_file) as f:
            yaml_data = f.read()
        self.config = yaml.load(yaml_data)
    def set_index(self):
        date=datetime.datetime.now().strftime(self.config['index_date_format'])
        self.index = self.render_j2(self.config['index'],index_date_format=date)
    def get_time_range(self, minutes_until_now):
        lte = int(time.time()) * 1000
        gte = (int(time.time()) - (minutes_until_now * 60)) * 1000
        self.range = dict(lte=lte, gte=gte, format="epoch_millis")
    def render_j2(self, string, **kwargs):
        t = Template(string)
        return t.render(**kwargs)
    def query(self,query_body,limit):
        res = self.es.search(index=self.index, body=query_body)
        ip_list = res['aggregations']['ip']['buckets']
        self.ip_list=self.process_resp(ip_list,limit)
    def process_resp(self,res,limit):
        d={}
        for doc in res:
            count = doc['doc_count']
            ip = doc['key']
            try:
                if count >= limit:
                    d[ip] = count
            except TypeError:
                print('count is: %s'%(count))
        return d.keys()

