import datetime
import pandas as pd
from .MySQLAux import MySQLAux
from .S3Aux import S3Aux
from .MailAux import MailAux


class ExecutionController():

    def __init__(self, database, control_table ='control_table',id_field='id_execution', s3_bucket='stone-project',TMP='/tmp/',use_controller=0):
        self.use_controller = use_controller
        if use_controller == 1:
            self.cnx = MySQLAux(database).connect()
            self.engine = MySQLAux(database).engine()
            self.start = datetime.datetime.now()
            self.finish = datetime.datetime.now()
            self.last_execution_id = pd.read_sql('SELECT max({}) FROM {}'.format(id_field,control_table),self.cnx)[id_field].values[0]
            self.last_status = pd.read_sql('SELECT status FROM {} WHERE {} = {}'.format(control_table,id_field,self.last_execution_id),self.cnx)['status'].values[0]
            self.filename = 'execution_log_{}.txt'.format(self.last_execution_id)
            self.remote_folder = 'logs'
            self.s3_link = 'https://{}.s3.amazonaws.com/{}/{}'.format(s3_bucket,self.remote_folder,self.filename)
        else:
            self.last_status='SUCCESS'


    def write_to_log(self,text):
        if self.use_controller == 1:
            f = open('{}/{}'.format(TMP, self.filename), 'w')
            f.write('{}      {}\n'.format(datetime.datetime.now(),text))
            f.close()

    def send_log_to_s3(self):
        if self.use_controller==1:
            s3 = S3Aux(s3_bucket)
            local_file = '{}/{}'.format(TMP, self.filename)
            remote_file = '{}/{}'.format(self.remote_folder,self.filename)
            s3.upload(local_file,remote_file)

    def start_new_execution(self):

        if self.use_controller==1:
            query = '''UPDATE {} set status ='FAILED' where status = 'RUNNING' '''.format(control_table)
            cursor = cnx.cursor()
            cursor.execute(query)
            cnx.commit()

            self.last_execution_id += 1 
            write_to_log('Starting Execution {}'.format(self.last_execution_id))
            send_log_to_s3()
            new_line = [
            {id_field:self.last_execution_id,
            'start':self.start,
            'finish':datetime.datetime(2099,1,1,0,0,0),
            's3_link':'{}'.format(s3_link),
            'status': 'RUNNING'}]
            df = pd.DataFrame(new_line)
            df.to_sql(control_table, engine, if_exists='append', index=False)

    def finish_execution(self):
        if self.use_controller==1:
            query_1 = '''UPDATE {} set status ='SUCCESS' where status = 'RUNNING' and {} = {} '''.format(control_table,id_field,self.last_execution_id)
            query_2 = '''UPDATE {} set finish ='{}' where status = 'SUCCESS' and {} = {} '''.format(control_table,self.finish,id_field,self.last_execution_id)
            cursor = cnx.cursor()
            cursor.execute(query_1)
            cnx.commit()
            cursor.execute(query_2)
            cnx.commit()
            write_to_log('Finishing Execution {}'.format(self.last_execution_id))
            send_log_to_s3()

    def set_to_fail(self):
        if self.use_controller==1:
            query_1 = '''UPDATE {} set status ='FAILED' where status = 'RUNNING' and {} = {} '''.format(control_table,id_field,self.last_execution_id)
            cursor = cnx.cursor()
            cursor.execute(query_1)
            cnx.commit()
    def send_mail(self):
        if self.use_controller==1:
            mail = MailAux()
            mail.send_mail('STONE-PROJECT-ERROR','Baixe o log aqui: {}'.format(self.s3_link),'MOVIES','mateusricardo94@gmail.com','mateus.ricardo@mobly.com.br')