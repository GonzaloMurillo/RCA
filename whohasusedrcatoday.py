import os
import glob
import sqlite3
import time

def retrieve_database_from_remote():
    print("Connecting to the remote machine to obtain the Telemetry DataBase")
    os.system('pscp gonzalo@10.207.84.149:/home/omkar/git/ctxdoing/backend/rca_telemetry.sqlite3 .')


if __name__=='__main__':
    os.system("cls")
    retrieve_database_from_remote()
    database_file=glob.glob('*.sqlite3')

    if(len(database_file)!=1):
        print("Something went wrong")
        exit(-1)
    else:
        print("Opening the file for analysis")
        conn=sqlite3.connect(str(database_file[0]))
        # Data for today in Year-month-day
        strings = time.strftime("%Y-%m-%d")
        query="SELECT distinct user_id from usage where timestamp like '%"+strings+"%'"
        #print("the query {}".format(query))

        cursor = conn.execute(query)
        print("Who has used the tool today...")
        for row in cursor:
            query2="select  email from users where id='"+str(row[0])+"'"
            #print("query2:{}".format(query2))
            cursor2=conn.execute(query2)
            for row2 in cursor2:
                print("User:{}".format(row2[0]))
            #print("id={}".format(row[0]))


