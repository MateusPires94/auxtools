from .MySQLAux import MySQLAux
import pandas as pd
import time

class PandasAux():

    def __init__(self, query, database):

        cnx = MySQLAux(database).connect()
        time.sleep(1)
        self.df = pd.read_sql(query, cnx)
        time.sleep(1)
        cnx.close()

    def fetch(self):

        return self.df

    def fetch_memory_optimized(self):

        df_int = self.df.select_dtypes(include=['int'])
        df_int = df_int.apply(pd.to_numeric,downcast='unsigned')
        self.df[df_int.columns] = df_int
        
        df_float = self.df.select_dtypes(include=['float'])
        df_float = df_float.apply(pd.to_numeric,downcast='float')    
        self.df[df_float.columns] = df_float
        
        df_obj = self.df.select_dtypes(include=['object']).copy()
        
        converted_obj = pd.DataFrame()
        for col in df_obj.columns:
            num_unique_values = len(df_obj[col].unique())
            num_total_values = len(df_obj[col])
            if num_unique_values / num_total_values < 0.5:
                converted_obj.loc[:,col] = df_obj[col].astype('category')
            else:
                converted_obj.loc[:,col] = df_obj[col]
        self.df[converted_obj.columns] = converted_obj
        
        del df_int
        del df_float
        del df_obj
        del converted_obj
        
        return self.df