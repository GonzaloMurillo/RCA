from util import version, logger
_log = logger.get_logger(__name__)

class DataDomain():

    current_autosupport_name="" # Contains the name of the autosupport from which the DataDomain object is build
    current_autosupport_content=[] # Contains a list with the current autosupport in memory (one line per entry)
    lrepl_client_time_stats=[] # Contains the part of the autosupport that is related with Lrepl Client Time Stats
    replication_contexts=[] # A list of dictionaries were each dictionary contains all the information of a replication context
    replication_contexts_frontend=[] # Another view of replication_contexts used for the communication with the front-end apps.
    num_of_replication_contexts=0 # This attribute contains the total number of replication contexts in the DataDomain

   # Constructor, it creates a DataDomain object from an autosupport file.
    def __init__(self,current_autosupport_name):
        self.current_autosupport_name=current_autosupport_name # A DataDomain object is build from an autosupport
        with open (self.current_autosupport_name) as autosupport_fd:
            self.current_autosupport_content=autosupport_fd.read().splitlines() # splitlines removes the \n from each line. We have now in self.current_autosupport_content the full autosupport

            self.populate_replication_contexts() # We call the method to populate the replication_contexts which will be a list of dictionaries
            self.populate_lrepl_client_time_stats("Lrepl client time stats","Lrepl client stream stats") # We call the method to populate the lrep_client_time_stats, indicating the delimitors in the autosupport that this information spreads
            self.populate_replication_contexts_frontend() # We call the method to populate the replication_context list of dictionaries in a way useful for the frontend
            self.hostname=""
            self.populate_hostname()
    # Object methods
   # This function method populates the replication_contexts class object with information about the replication contexts
    def populate_replication_contexts(self):

        context={} # Dictionary that contains one specific context that has being read from the autosupport
        #Example
        #context={'ctx_number':'0','src_host':'dd640.datadomain.com','src_path':'/data/col1/source','dst_host':'dd890.datadomain.com','dst_path':'/data/col1/destination'}

        context_list=[] # A list of contexts, each of them being a dictionary
        self.replication_contexts=[]

        for autosupport_read_line in self.current_autosupport_content: # We read from all the autosupport
            if(len(autosupport_read_line)!=0): # If the line is empty we discard it
                if 'repl.' in autosupport_read_line and ('src_' in autosupport_read_line or 'dst_' in autosupport_read_line): # If it contains information about context (both source and destination)
                    #Example of what is inside autosupport_read_line
                    #repl.001.dst_host = DD7200-1-SH.localdomain
                    #repl.001.src_path = /data/col1/replication1
                    context_list=autosupport_read_line.split('=') #We split by the symbol =
                    if 'repl' in context_list[0]: # There is always repl, we just want to obtain the replication context
                        w=context_list[0].split('.') # We split the first part by the symbol .
                        context['ctx_number']=int(w[1]) # The context number is always after the first .

                        for tt in w: # Now we search if is a source replication context, or a destination replication context
                            if 'src_host' in tt:
                                context['src_host']=context_list[1].strip() # we use strip to remove any space at the beggining or end
                                self.replication_contexts.append(context)
                            elif 'src_path' in tt:
                                context['src_path']=context_list[1].strip()
                                self.replication_contexts.append(context)

                            elif 'dst_host' in tt:
                                context['dst_host']=context_list[1].strip()
                                self.replication_contexts.append(context)

                            elif 'dst_path' in tt:
                                    context['dst_path']=context_list[1].strip()
                                    self.replication_contexts.append(context)
                        context={}

        # Now I am changing the format, so self.replication_contexts is a list of Dictionaries
        # where each dictionary in the list represents fully a unique content.
        # in contrast with what we have right now where there are several dictionaries across the list
        # representing different just part of the information from a replication context and the view is not clear
        context_list=[]
        context_list_unique=[]

        # I obtain a list with the number of contexts
        for itera in self.replication_contexts: # itera is an iterator dictionary
            context_list.append(itera['ctx_number'])
        list_set=set(context_list) # I need to obtain just unique values, so I make a set
        context_list_unique=list(list_set) # and from that set a list
        self.num_of_replication_contexts=len(context_list_unique) # I update the class attribute num_of_replication_contexts

        # Here is where I do start to change the representation view
        temporal_context={}
        temporal_list=[]
        for i in context_list_unique: # for each context
            for j in self.replication_contexts: # I do search in the old format list of dictionaries

                if j["ctx_number"]==i:
                    temporal_context['ctx_number']=i
                    if 'src_host' in j: # checking if the key is in the dictionary
                        temporal_context['src_host']=j['src_host']

                    if 'src_path' in j:
                        temporal_context['src_path']=j['src_path']

                    if 'dst_host' in j:
                        temporal_context['dst_host']=j['dst_host']

                    if 'dst_path' in j:
                        temporal_context['dst_path']=j['dst_path']

            temporal_list.append(temporal_context) # temporal context here contains a dictionary with the full information of a context, so we add to the list
            temporal_context={} # we clear the dictionary as we are going to iterate to the next context
        self.replication_contexts=temporal_list # when we have finish we update the class attribute replication_contexts
        _log.info("This is the list of replication contexts found {}".format(self.replication_contexts))
    # This function transfor the context passed as a parameter in a dictionary in the form required by the asup_analysis_apis.py
    #context={'ctx': 1,
    #             'source': {
    #                 'host': 'dd390gcsr01.nam.nsroot.net',
    #                 'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep',
    #                 },
    #             'destination': {
    #                 'host': 'dd390gcsr02.nam.nsroot.net',
    #                 'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'
    #                }
    def get_repl_ctx_list_frontend(self,context_number):

        context={}
        context['ctx']=context_number
        src_host=""
        src_path=""
        dst_host=""
        dst_path=""
        for itera in self.replication_contexts:
            if(itera["ctx_number"]==context_number): # We have foud the key for the context we are searching, we just need to reformat it
                if 'src_host' in itera:
                    src_host=itera['src_host']
                if 'src_path' in itera:
                    src_path=itera['src_path']
                if 'dst_host' in itera:
                    dst_host=itera['dst_host']
                if 'dst_path' in itera:
                    dst_path=itera['dst_path']
                # We can exit the bucle once we find the replication context, as the context number is a primary key and replication_contexts is ordered
                #break
        context['ctx']=context_number
        context['source']={'host':src_host,'mtree':src_path}
        context['destination']={'host':dst_host,'mtree':dst_path}
        return context

    # We use this function for creating an structure of just the contexts that need to be displayed in the get_repl_ctx_list_frontend
    # Those contexts are the contexts from which we hace Lrepl client time stats
    def populate_replication_contexts_frontend(self):
        _log.info("Num of replication contexts:{}".format(self.num_of_replication_contexts))
        for context in self.replication_contexts:
            _log.info("A context that we are trying to identify if is useful for the front-end:{}".format(context['ctx_number']))  #Is useful if it is a context that we have lrepl client time stats data.
            if(self.is_source_context(context['ctx_number'])):
                self.replication_contexts_frontend.append(self.get_repl_ctx_list_frontend(context['ctx_number'])) # Asi solo si son secuenciales los contextos

    # We need a function to know if a context is valid for calculating the times and graphs, and is only valid if there is lrepl client time stats info
    # which normally means that is a source context and hence the name of the function, but sometimes, even a source context has no valid lrepl_client_time_stats
    # because there are too many contexts and lrepl client time stats is not calculated for all of them, or because all the metrics are 0
    def is_source_context(self,i):
        _log.info("Information of Lrepl client time stats {}".format(self.lrepl_client_time_stats))
        context_string="rctx://"+str(i)

        _log.info("Searching for context:{}".format(context_string))
        _log.info("We are searching in: {}".format(self.lrepl_client_time_stats))

        for read_context in self.lrepl_client_time_stats:

            _log.info("Context string:{} compared with {}".format(context_string,read_context[0]))
            if(context_string in read_context[0]): # index 0 from the second list is the context number, for the first one is the header
                _log.info("NICE!:The context:{}, is a replication context we have lrepl client time stats info".format(context_string))
                # We could check here if the times of the contexts sum 0 and do not display then, but we have not done it, we display them as empty (which I think is better)
                return True
        # At this level of indentation we have traversed all the list and there is no lrepl client time stat information for the context
        _log.info("SORRY!:The context:{}, is a replication context we DO NOT have lrepl client time stats info".format(context_string))
        return False

    # This function prints an specific replication context
    def print_replication_context(self,context_number):
        # Toda la informacion del contexto 1
        for itera in self.replication_contexts:
            if(itera["ctx_number"]==context_number):
                if 'src_host' in itera:
                    print('src_host:{}').format(itera['src_host'])
                if 'src_path' in itera:
                    print('src_path:{}').format(itera['src_path'])
                if 'dst_host' in itera:
                    print('dst_host:{} ').format(itera['dst_host'])
                if 'dst_path' in itera:
                    print('dst_path:{}').format(itera['dst_path'])


    # Returns a list with the information of an specific context lrepl_client_time_stats
    def get_lrepl_client_time_stats(self,replication_context_number):
        context_to_search="rctx://"+str(replication_context_number)
        for i in range(1,len(self.lrepl_client_time_stats)): # We start in 1 as 0 is the header containing info about each column header
            if self.lrepl_client_time_stats[i][0]==context_to_search:
                return(self.lrepl_client_time_stats[i])

    # This method populates the lrep_client_time_stats class member that contains the portion of the autosupport where there is the Lrepl client time stats info
    def populate_lrepl_client_time_stats(self,start_delimiter,end_delimiter):

        found_start = False # A trigger variable
        found_end = False # Trigger variable
        data=[] # A list storing the information that we are reading from the autosupport

        # We are searching for the information about the contexts, and that is stored in the autosupport
        # between the delimiters 'Lrepl client time stats' and 'Lrepl client stream stats'
        # those delimiters can be changing with DD OS Version, be aware!

        with open (self.current_autosupport_name) as autosupport_file:
            for line in autosupport_file:
                if start_delimiter in line:  # We found the start_delimiter, now we search until the start of the Lrepl client time stats
                    print(line)
                    found_start = True
                    for line in autosupport_file:  # And once we find it, we read until the end of the relevant information (
                        if end_delimiter in line:  # We exit here as we have all the information we need
                            found_end=True
                            break
                        else:

                            if not (line.isspace()): # We do not want to add to the data empty strings, so we ensure the line is not empty
                                data.append(line.replace(',','').strip().split())  # We store information in a list called data we do not want ','' or spaces
        if(found_start and found_end):
            self.lrepl_client_time_stats=data # now lrepl_client_time_stats contains the information found in the autosupport about lrepl_client_time_stats
        else:
            return (-1)

    # We need to know the hostname of the DataDomain as obtained from the autosupport, and this object method is precisely for that
    def populate_hostname(self):
        with open (self.current_autosupport_name) as autosupport_file:
            for line in autosupport_file:
                if 'HOSTNAME' in line:
                     aux=line.split("=")
                     aux_hostname=aux[1].strip()
                     self.hostname=aux_hostname
                     break
    # function give_me_position_in_header_of
    # We use this function beause some times the order in the columns that represent lrepl client time stats, change
    # from DD OS version to DD OS version, so we cannot rely on a fixed position. This function returns dinamically the position.

    def give_me_position_in_header_of(self,column_name):
        self.column_name=column_name
        pos=0
        for i in self.lrepl_client_time_stats[0]:
            _log.info("Searching for position of column:{}".format(column_name))
            _log.info("Returned:{}".format(i))
            if(column_name in i): # Sometimes the field name changes for example send_sketches in a DD OS 6.1.1.20 is delta_send_sketches in 5.7.4 and therefore the in, instead of the == operator
                _log.info("Found in position:{}".format(pos))
                return pos
            else:
                pos=pos+1

        # If we have arrived here is that we have not found that column_name
        return (-1)
