import pandas as pd
import sqlalchemy
import mysql.connector

def get_market_data():

    db_info = pd.read_pickle("user_info.pkl")
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=db_info.loc['host'].value
    , db='firedb', user=db_info.loc['user'].value, pw=db_info.loc['password'].value))

    yearly_market_df = pd.read_sql_table('yearly_market_df', engine) 

    yearly_market_df = yearly_market_df.set_index('Year')
    return yearly_market_df


def load_new_user_profile(user_var_series):
    db_info = pd.read_pickle("user_info.pkl")
    mydb = mysql.connector.connect(host=db_info.loc['host'].value, database = 'firedb'
    , user=db_info.loc['user'].value, passwd=db_info.loc['password'].value,use_pure=True)

    str_cols = str(tuple(user_var_series.index.values))
    str_cols = str_cols.replace("'","")

    mycursor = mydb.cursor()

    sql = f"REPLACE INTO user_fire_report_info {str_cols} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = tuple(user_var_series.values)
    mycursor.execute(sql, val)
    mydb.commit()

    # print(mycursor.rowcount, "record inserted.")
    mydb.close()

def return_user_profile(user_id):
    db_info = pd.read_pickle("user_info.pkl")
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=db_info.loc['host'].value
    , db='firedb', user=db_info.loc['user'].value, pw=db_info.loc['password'].value))

    user_id_df = pd.read_sql_query(f'SELECT * FROM user_fire_report_info WHERE user_id = "{user_id}"', engine)
    return user_id_df