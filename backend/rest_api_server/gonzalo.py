#from auxiliar import datadomain
#datadomain.DataDomain("autosupport")
import os
from auxiliar.newdatadomain import DataDomain
path=r"C:\DDTOOLS-master\ctxdoing-master-branch\ctxdoing\backend\autosupport"
print(path)
#print(os.path.abspath(path))
#print(os.path.basename(path))
gonzalo=DataDomain(os.path.abspath(path))
#gonzalo.print_replication_context(1)
#ekbote=[]
#ekbote.append(gonzalo.ekbote(1))
#ekbote.append(gonzalo.ekbote(2))

#print(ekbote)
#print(gonzalo.replication_contexts_frontend)

#for i in range(0,gonzalo.num_of_replication_contexts):
#    if gonzalo.is_source_context(i):
#        print  gonzalo.replication_contexts_frontend[i]


#print("-----------------------\n")
#print(gonzalo.replication_contexts_frontend)
#print(gonzalo.hostname)

#if('ctx' in gonzalo.replication_contexts_frontend):
#    print("si")
nuevo={}
for itera_dic in gonzalo.replication_contexts_frontend:
    if 'ctx' in itera_dic:
        if(1 in itera_dic.values()):
            nuevo['ctxDetails']=itera_dic
            nuevo['ctxUsageTime']={'key':'Total time spent','value':'111','unit':"seconds"}

print(nuevo)
