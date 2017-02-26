import yaml
import redis
from jinja2 import Template
import os
from _datetime import datetime
import logging
import ipaddress
from apscheduler.schedulers.background import BlockingScheduler
#from apscheduler.schedulers.background import BackgroundScheduler
#import signal


class TaskerDo:
    '''
    schedule template to file generation based on redis
    '''
    ip_list =[]
    def __init__(self, conf_file):
        self.get_configuration(conf_file)
        self.client = redis.Redis(**self.config['settings']['redis'])
        self.set_logging(self.config['settings']['logfile'])
        self.sched = BlockingScheduler()
        self.set_scheduler(self.run, self.config['generate']['schedule'])

    def set_scheduler(self,job,schedule,args=None):
        '''
        set schedual jobs
        :param schedule: dict, contain 'name', 'trigger' =[cron|interval|more apscheduler on web] , and params minuts,second, and more on apscheduler
        :return: None
        '''
        self.sched.add_job(job, args=args,trigger=schedule['trigger'], name=schedule['name'],**schedule['params'])


    def stat(self):
        self.sched.start()

    def stop(self):
            self.sched.shutdown()

    def run(self):
        '''
        This is where the magic starts and all the jobs been executed.
          optional load ip_list to redis,
          get ips from redis -> generate file -> run reload job
        :param ip_list: optional, list of ip to loan into redis
        :return: nothing yet
        '''
        if len(self.ip_list) > 0:
            self.redis_push_ip_list(self.ip_list, expiration=self.config['bad_ip_expiration'])
            self.ip_list = []
        ip_list = self.redis_get_ip_list()
        logging.info("%s items in database: %s" % (len(ip_list), ",".join(ip_list)))
        if len(ip_list) > 0:
            generate = self.config['generate']
            status = self.file_generate(template_file=generate['template'],generated_file=generate['file'], ip_list=ip_list)
            if status:
                logging.info("configuration file: %s was created"%(generate['file']))
                for command in self.config['generate']['reload_commands']:
                    logging.info("executing command: %s" % (command))
                    try:
                        if self.reload_services(command):
                            logging.info("Success")
                    except CommanFail as e:
                        self.logger.error(e)
                        break
            else:
                logging.info('reload not needed')

    def is_diff(self, content_str, current_file):
        '''
        Compair new version to existing one
        :param content_str: string, new version content string
        :param current_file: file, existing file
        :return: bool, true is different
        '''
        try:
            with open(current_file) as f:
                current_str = f.read()
        except FileNotFoundError:
            return True
        if content_str == current_str:
            return False
        else:
            return True

    def get_configuration(self, conf_file):
        '''
        :param conf_file: yaml configuration file with report data
        :return: configuration data
        '''
        with open(conf_file) as f:
            yaml_data = f.read()
        self.config = yaml.load(yaml_data)

    def set_logging(self, log_file):
        self.logger = logging.getLogger()
        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def file_generate(self, template_file, generated_file, **kwargs):
        '''
        generate application config file using template
        :param template_file: file, the template file to generate using Jinja2 template engine
        :param generated_file: file, the file to generate
        :param kwargs: the argument to send to templates
        :return: bool status
        '''
        with open(template_file) as t:
            template_str = t.read()
        t = Template(template_str)
        content_str = t.render(**kwargs)
        is_diff = self.is_diff(content_str, generated_file)
        if is_diff:
            return self.write_content(content_str, generated_file)
            logging.info("New version exist")
        else:
            logging.info("No changes in current file, generation not needed")
            return False

    def redis_push_ip_list(self, ip_list, expiration):
        '''
        push list of ip's to redis and set expiration
        :param ip_list: list of strings
        :param expiration: int second
        :return: bool status
        '''
        ip_list = [ip for ip in ip_list if ipaddress.ip_address(ip).is_global]
        if len(ip_list) == 0:
            raise ValueError('Empty list supplied')
        for key in ip_list:
            _ = self.client.set(key, None, ex=expiration)
        return True

    def redis_get_ip_list(self):
        '''
        get the list of ips from redis
        :return: list
        '''
        ips = self.client.keys('*')
        return [i.decode() for i in ips]

    def write_content(self, content_str, generated_file, backup=True):
        '''
        helper to generate_file function, write the data to file and create backup file
        :param content_str: string, the generated content
        :param generated_file:
        :param backup: bool
        :return: bool, status
        '''
        if backup and os.path.exists(generated_file):
            date = datetime.now().strftime('%y%m%d%H%M%S')
            os.rename(generated_file, generated_file + '.' + date)
        with open(generated_file, 'w') as conf_file:
            _ = conf_file.write(content_str)
        return True

    def reload_services(self, commands_list):
        '''
        list of command_str to execute, stop if one failed
        :param commands_list: list of shell command_str
        :return: bool, status
        '''
        for command_str in commands_list:
            exit_status = os.system(command_str)
            if exit_status > 0:
                raise CommanFail("Command %s failed with status %s" % (command_str, exit_status))
        return True


class CommanFail(Exception):
    pass



