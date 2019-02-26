#!/usr/bin/env python
# coding=utf-8
from util import version, logger
from rest_api_server.dellemc.replicationcontextplot import ReplicationContextPlot
from rest_api_server.dellemc.pdfhelper import PDFHelper
# from pdfhelper import PDFHelper
import os,datetime
_log = logger.get_logger(__name__)


class DataDomain():
    """
    A class used to represent a Data Domain Object

    ...

    Attributes
    ----------
    current_autosupport_name : str
        an string that contains the name of the autosupport file

    current_autosupport_content : list
        The autosupport file in memory. Each item in the list is a line of the autosupport

    lrepl_client_time_stats : list
        A list that contains the part of the autosupport that is related with Lrepl Client Time Stats

    replication context: list
        A list of dictionaries were each dictionary contains all the information of a replication context

    replication_context_frontend: list
        A list containing the replication context in a format that the front end understands.

    num_of_replication_contexts : int
        The total number of replication contexts in the DataDomain object

    hostname:   str
    The name of the DataDomain obtained from the autosupport

    serial_number: str
    The serial number of the DataDomain obtained from the autosupport


    Methods
    -------
    populate_private_members()
        Traverses the list current_autosupport_content, searching for the parameters of the autosupport that are important for the objectives of the class.
    """

   # Constructor, it creates a DataDomain object from an autosupport file.

    def __init__(self):
        """Class constructor, just initializes the parameter class members

        Args:
        none
        Returns:
        none

        """
        self.current_autosupport_name=""
        self.current_autosupport_content=[]
        self.lrepl_client_time_stats=[]
        self.lrepl_client_time_stats_delta_difference=[]
        self.replication_contexts=[]
        self.replication_contexts_frontend=[]
        self.num_of_replication_contexts=0
        self.hostname=""
        self.serial_number=""
        return

    # Object methods

    def use_asup_file(self, filename):
        """Loads an autosupport file into the memory list current_autosupport_content.

        Args:
        filename (str): The name of the autosupport file

        Returns:
        none:

        """
        self.current_autosupport_name=filename # A DataDomain object is build from an autosupport
        with open (self.current_autosupport_name,'r') as autosupport_fd:

            # We read the autosupport file and put it in memory, class variable member current_autosupport_content
            self.current_autosupport_content=autosupport_fd.read().splitlines() # splitlines removes the \n from each line. We have now in self.current_autosupport_content the full autosupport



    def parse_asup_file_for_replication_contexts_info(self):

        """Parses the asup file searching in the registry for replication contexts.
        For detecting the replication contexts, we search for repl.xxx registry keys.

        Args:
        none
        Returns:
        none:Updates private members of the class, like self.serial_number, self.hostname, self.replication_contexts

        """



        context={} # Dictionary that contains one specific context that has being read from the autosupport
        #Example
        #context={'ctx_number':'0','src_host':'dd640.datadomain.com','src_path':'/data/col1/source','dst_host':'dd890.datadomain.com','dst_path':'/data/col1/destination'}
        context_list=[] # A list of contexts, each of the items in the list will be a context dictionary
        #self.replication_contexts=[]

        # I do not want to read the file twice, so until I arrive to where the replication context information is located in the file, I read some data that will be useful
        # and populate the private members of the class with that info.

        for autosupport_read_line in self.current_autosupport_content: # We read from all the autosupport list
            if(len(autosupport_read_line)!=0): # If the line is empty we discard it

                if "SYSTEM_SERIALNO=" in autosupport_read_line:
                    splitted_serial=autosupport_read_line.split("=")
                    self.serial_number=splitted_serial[1]

                if "HOSTNAME=" in autosupport_read_line:
                    splitted_hostname=autosupport_read_line.split("=")
                    self.hostname=splitted_hostname[1]
                # Here is where we have read a registry key for a replication context.
                if 'repl.' in autosupport_read_line and ('src_' in autosupport_read_line or 'dst_' in autosupport_read_line): # If it contains information about context (both source and destination)
                    #Example of what is inside autosupport_read_line
                    #repl.001.dst_host = DD7200-1-SH.localdomain
                    #repl.001.src_path = /data/col1/replication1
                    context_list=autosupport_read_line.split('=') #We split by the symbol =
                    if 'repl' in context_list[0]: # There is always repl, we just want to obtain the replication context
                        replication_registry_key_left_part=context_list[0].split('.') # We split the first part by the symbol .
                        context['ctx_number']=int(replication_registry_key_left_part[1]) # The context number is always after the first '.'

                        for replication_registry_subkey in replication_registry_key_left_part: # Now we search if is a source replication context, or a destination replication context
                            if 'src_host' in replication_registry_subkey:
                                context['src_host']=context_list[1].strip() # we use strip to remove any space at the beggining or end
                                self.replication_contexts.append(context)
                            elif 'src_path' in replication_registry_subkey:
                                context['src_path']=context_list[1].strip()
                                self.replication_contexts.append(context)

                            elif 'dst_host' in replication_registry_subkey:
                                context['dst_host']=context_list[1].strip()
                                self.replication_contexts.append(context)

                            elif 'dst_path' in replication_registry_subkey:
                                    context['dst_path']=context_list[1].strip()
                                    self.replication_contexts.append(context)
                        context={}
        _log.debug("Before changing format: {}".format(self.replication_contexts))
        self.change_format()
        _log.debug("After changing format: {}".format(self.replication_contexts))

        # We parse now for lrepl_client_time_stats information and populate the list of front_end_contexts
        self.__parse_asup_file_for_lrepl_client_time_stats("Lrepl client time stats","Lrepl client stream stats")
        self.__populate_front_end_contexts()



    def change_format(self):
        """Changes the format of the class member self.replication_contexts
        We do this because we want to have a list of dictionaries where each dictionary in the list represents a fully context
        In contrast, what we have before the change of the format is several dictionaries across the list representing different
        parts of the information for a single replication context. So before the change of format, we need to traverse the whole list for finding
        information just about 1 context. That is the motivation for changing the format.

        Args:
        none

        Returns:
        Updates self.replication_contexts && self.num_of_replication_contexts

        """
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
        _log.debug("This is the list of replication contexts found {}".format(self.replication_contexts))

    def get_repl_ctx_list_frontend(self,context_number):

        """This function transforms the context passed as a parameter in a dictionary that looks like what the frontend is expecting, which is the following format:
        context={'ctx': 1,
                     'source': {
                         'host': 'dd390gcsr01.nam.nsroot.net',
                         'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep',
                         },
                     'destination': {
                         'host': 'dd390gcsr02.nam.nsroot.net',
                         'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'
                        }

        Args:
        context_number:int
        The number of the replication context to trasform
        Returns:
        context: dic
        A dictionary representing the context in the format expected by the frontend.
        """
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

    def is_source_context(self,i):

        """We use this function to know if a context is valid for calculating the times and graphs. A replication context is only valid if there are lrepl client time stats info
        which normally means that is a source context (although some source contexts do not have lrepl client time stats information and therefore we neex extra check)
        One thing to notice is that if there are a lot of replication context, the File System, does not calculate the lrepl client time stats for all of them, so we do not want
        contexts with all the columns in lrepl client time stats set to 0
        Args:
        i: integer

        Returns:
        True: if we have Lrepl client time stats information for the context i
        False: if we do not have Lrepl client time stats information for the context i

        """
        total=0
        _log.debug("Information of Lrepl client time stats {}".format(self.lrepl_client_time_stats))
        context_string="rctx://"+str(i)

        _log.debug("Searching for context:{}".format(context_string))
        _log.debug("We are searching in: {}".format(self.lrepl_client_time_stats))

        for read_context in self.lrepl_client_time_stats:

            _log.debug("Context string:{} compared with {}".format(context_string,read_context[0]))
            if(context_string.strip()==read_context[0].strip()): # index 0 from the second list is the context number, for the first one is the header. #Needs
                _log.debug("NICE!:The context:{}, is a replication context we have lrepl client time stats info".format(context_string))
                # This is a check to avoid replication context where all the lrepl client time stats added sum 0
                # Can be commented, if we want to display contexts without lrepl client time stats.
                for t in range(1,len(read_context)):
                    total=total+int(read_context[t])
                if(total!=0):
                        return True # As we have information in lrepl client time stats and the columns together not add 0


        else:
            # At this level of indentation we have traversed all the list and there is no lrepl client time stat information for the context

            _log.debug("SORRY!:The context:{}, is a replication context we DO NOT have lrepl client time stats info".format(context_string))
            return False



    def print_replication_context(self,context_number):
        """ prints information about the replication context pased as parameter

        src_host,src_path,dst_host,dst_path
        Args:
        context_number:int

        Returns:
        none

        Just prints the information about the context number

        """
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



    def get_lrepl_client_time_stats(self,replication_context_number):
        """ Returns a list with the information of an specific context lrepl_client_time_stats

        Args:
        replication_context_number:int

        Returns:
        self.lrepl_client_time_stats[i]:list

        It returns a list with the information of the lrepl_client_time_stats for the context specified in the parameter replication_context_number

        """
        context_to_search="rctx://"+str(replication_context_number)
        for i in range(1,len(self.lrepl_client_time_stats)): # We start in 1 as 0 is the header containing info about each column header
            if self.lrepl_client_time_stats[i][0]==context_to_search:
                return(self.lrepl_client_time_stats[i])

    # This method populates the lrep_client_time_stats class member that contains the portion of the autosupport where there is the Lrepl client time stats info

    def __parse_asup_file_for_lrepl_client_time_stats(self,start_delimiter,end_delimiter):

        """ This is a private method to parse the file just for the lrepl client time stats metrics

        Args:
        start_delimiter:str
        end_delimiter:str

        It searches the autosupport file between the start_delimited and end_delimiter and populates self.lrepl_client_time_stats with the information found.
        Returns:
        none

        It updates self.lrepl_client_time_stats with Lrepl Client Time Stats information


        """
        found_start = False # A trigger variable
        found_end = False # Trigger variable
        data=[] # A list storing the information that we are reading from the autosupport

        # We are searching for the information about the contexts, and that is stored in the autosupport
        # between the delimiters 'Lrepl client time stats' and 'Lrepl client stream stats'
        # those delimiters can be changing with DD OS Version, be aware!
        _log.warning("The name of the autosupport file for calculating lrepl_client_time_stats:{}".format(self.current_autosupport_name))
        with open (self.current_autosupport_name,'r') as autosupport_file:
            for line in autosupport_file:
                if start_delimiter in line:  # We found the start_delimiter, now we search until the start of the Lrepl client time stats

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
    def __populate_front_end_contexts(self):
        """ It does populate the self.replication_contexts_frontend with just the context that are suitable to be displayed (and selected) in the frontend.

        Args:
        none

        Returns:
        none

        It updates self.replication_contexts_frontend with the information about the context. source_host|source_path|destination_host|destination_path

        """
        _log.debug("Num of replication contexts:{}".format(self.num_of_replication_contexts))
        for context in self.replication_contexts:
            _log.debug("A context that we are trying to identify if is useful for the front-end:{}".format(context['ctx_number']))  #Is useful if it is a context that we have lrepl client time stats data.
            if(self.is_source_context(context['ctx_number'])):
                self.replication_contexts_frontend.append(self.get_repl_ctx_list_frontend(context['ctx_number']))


    def get_hostname(self):
        """Returns the hostname contained in the autosupport


        Args:
        none
        Returns:
        self.hostname:string

        An string with the name of the host obtained from the autosupport

        """
        if self.hostname:
            return self.hostname

    def get_serial(self):
        """Returns the serial number contained in the autosupport
            Args:
            none
            Returns:
            self.serial_number:string

            An string with the serial obtained from the autosupport

        """
        if self.serial_number:
            return self.serial_number

    def get_generated_on(self):
        """Returns the GENERATED_ON date contained in the autosupport
            Args:
            none: It takes the filename from the self.current_autosupport_name
            Returns:
            generated_on_date:string

            An string with the serial obtained from the autosupport

        """
        for autosupport_read_line in self.current_autosupport_content: # We read from all the autosupport list
            if(len(autosupport_read_line)!=0): # If the line is empty we discard it

                if "GENERATED_ON=" in autosupport_read_line:

                    splitted_generated=autosupport_read_line.split("=") # We get just the date and not the string GENERATED_ON
                    date_time_str_splitted=splitted_generated[1].split() # We split the part that is the date, because we do not want time zone (simplification)
                    date_time_str_aux=date_time_str_splitted[0]+" "+date_time_str_splitted[1]+" "+date_time_str_splitted[2]+" "+date_time_str_splitted[5]+" "+date_time_str_splitted[3] # We build something that can be understood by the frontend
                    _log.debug("GENERATED DATE FOUND {}".format(date_time_str_aux))
                    return date_time_str_aux


    def calculate_delta_difference(self,dd_older):

        def find_context_in_older(which_context,dd_older):
            _log.debug("Method calculate_delta_difference:find_context_in_older")
            _log.debug("Displaying dd_older.lrepl_client_time_stats {}".format(dd_older.lrepl_client_time_stats))
            #_log.debug("We are trying to find {} in dd_older.lrepl_client_time_stats {}".format(which_context),dd_older.lrepl_client_time_stats)

            for iterator in range (1,len(dd_older.lrepl_client_time_stats)):

                for reiterator in dd_older.lrepl_client_time_stats[iterator]:

                    if "rctx" in reiterator: # We do not want to search in fields containing numeric values
                        _log.debug("Method calculate_delta_difference:find_context_in_older. Comparing {} with {}".format(which_context,reiterator))
                        if reiterator==which_context:
                            _log.debug("We found the context that we were searching for {}, we are going to return the lrepl_client_time_stats {}".format(which_context,dd_older.lrepl_client_time_stats[iterator]))
                            return dd_older.lrepl_client_time_stats[iterator]

            return -1 # If we arrive here is that the information of the context is not found

        def substract(context_newer,context_older,the_context):
            context_substracted=[]
            context_substracted.append(the_context)
            _log.debug("Method calculate_delta_difference:substract")
            _log.debug("We are going to calculate the difference between {} and {}".format(context_newer,context_older))
            for it in range(1,len(context_newer)):
                context_substracted.append(int(context_newer[it])-int(context_older[it])) # We substract every field)

            _log.debug("Method calculate_delta_difference:substract")
            _log.debug("What we are returning from the substract operation:{}".format(context_substracted))
            return(context_substracted)


        _log.debug("Method calculate_delta_difference:We enter the method to calculate the delta difference")
        _log.debug("Method calculate_delta_difference:Newer Lrepl client time stats")
        print(self.lrepl_client_time_stats)
        _log.debug("Method calculate_delta_difference:Older Lrepl client time stats")
        print(dd_older.lrepl_client_time_stats)

        if len(self.lrepl_client_time_stats[0])==len(dd_older.lrepl_client_time_stats[0]): # We are good to go as both autosupport have the same number of lprel_client_time_stats_columns (field 0 is the header)
            _log.debug("Method calculate_delta_difference: The two autosupport have the same number of columns in lrepl_client_time_stats")
            # We just calculate delta difference for the same contexts, we do not asume that if a context is present in one autosupport and in the other, is not the same
            for i in range (1,len(self.lrepl_client_time_stats)): # each i starting in 1, is information of a context
                for j in self.lrepl_client_time_stats[i]:
                    if "rctx:" in j: # We need to search that context in the dd_older.lrepl_client_time_stats
                        list_with_lrepl_client_time_stats_context_in_older_asup=find_context_in_older(j,dd_older) # The contexts has being found
                        _log.debug("Method calculate_delta_difference:What has been returned by find_context_in_older {}".format(list_with_lrepl_client_time_stats_context_in_older_asup))
                        if list_with_lrepl_client_time_stats_context_in_older_asup!=-1:
                             resultado=[]
                             resultado=substract(self.lrepl_client_time_stats[i],list_with_lrepl_client_time_stats_context_in_older_asup,j)
                             _log.debug("Resultado:{}".format(resultado))
                             self.lrepl_client_time_stats_delta_difference.append(resultado)
        _log.debug("The lrepl_client_time_stats_delta_difference {}".format(self.lrepl_client_time_stats_delta_difference))

    def return_lrepl_client_time_stats_delta(self):
        return self.lrepl_client_time_stats_delta_difference


    def make_lrepl_client_time_stats_equal_to_delta_time_stats(self):
        self.lrepl_client_time_stats=self.lrepl_client_time_stats_delta_difference

    def give_me_position_in_header_of(self,column_name):
        """We use this function beause some times the order in the columns that represent lrepl client time stats, change
           from DD OS version to DD OS version, so we cannot rely on a fixed position. This function returns dinamically the position of a column name, so we can use it to access a list by index.
            Args:
            column_name: string

            name of the column we want to obtain the position for
            Returns:
            integer: representing index position or -1 if not found

            """
        self.column_name=column_name
        pos=0
        for i in self.lrepl_client_time_stats[0]:
            _log.debug("Searching for position of column:{}".format(column_name))
            _log.debug("Returned:{}".format(i))
            if(column_name in i): # Sometimes the field name changes for example send_sketches in a DD OS 6.1.1.20 is delta_send_sketches in 5.7.4 and therefore the in, instead of the == operator
                _log.debug("Found in position:{}".format(pos))
                return pos
            else:
                pos=pos+1

        # If we have arrived here is that we have not found that column_name
        return (-1)


    def get_replication_analysis(self,selected_replication_contexts,app):

        """
                The function receives from the front ent the replication context selected and performs the analysis and calls the class ReplicationContextPlot to plot the graphs

                Args:
                selected_replication_contexts: list

                A list of the replication contexts to analyze_replication_contexts

                Returns:
                final_data_structure: a list of dictionary structure in a format that the frontend understands.


        """
        final_data_structure=[] # This is the final structure that we are going to build
        _log.debug("START of the method to analyze the contexts provided")
        _log.debug("The selected replication context that need analysis are:{}".format(selected_replication_contexts))
         # We iterate between the selected replication contexts

        for itera_dict in selected_replication_contexts: # selected_replication_contexts is the info that comes from the selection context screen


             _log.debug("itera dict:{}".format(itera_dict))

             dic_auxiliar={}
             dic_auxiliar['ctxDetails']=itera_dict # We add to the dic auxiliar the key {'ctxDetails'} that will contain the details of the context
             list_ctx_usage_time=[] # This list will contain the context lrepl client time stats values

             aux_lrepl_client_time_stats=[] # This list is going to content the lrepl client time stats of that particular context
             # Now we need to obtain the lrepl_client_time_stats for the context that we are analyzing. That info is already in the DataDomain object because the constructor does
             for i in range(1,len(self.lrepl_client_time_stats)): # We start in 1, because dd,lrepl_client_time_stats[0], just contains the header
                 searching_for="rctx://"+str(itera_dict['ctx'])
                 _log.debug("We are searching the Lrepl client time stats of context:{}".format(searching_for))

                 if(self.lrepl_client_time_stats[i][0]==searching_for): # We are searching for on one of the specific contexts selected for analysis
                     _log.debug("We have foud the lrepl_client_time_stats of the context {}".format(searching_for))
                     # We found it, so we make the aux_lrepl_client_time_stats equal to the list that corresponds in the dd object
                     aux_lrepl_client_time_stats=self.lrepl_client_time_stats[i]
                     # And we exit
                     break
             _log.debug("The list aux_lrepl_client_time_stats for the contex:{} now contains{}".format(searching_for,aux_lrepl_client_time_stats))

             # We do the maths as we are using relative values instead of relying on the calculation coming in the autosupport
             sum=0
             for x in range(2,len(aux_lrepl_client_time_stats)): # we start in 2, because 0, is the ctx number, and 1 is the calculated by the dd lrepl client time stats, we do not trust it as it fails from time to time, so we add the times together ourselves

                 sum=sum+int(aux_lrepl_client_time_stats[x])

             _log.debug("The total time spent by context {} is {} as calculated by adding together all the values".format(searching_for,sum))
             total_computed_time=sum

             if total_computed_time==0: # We cannot calculate anything if the time of all the metrics is 0, this context has no info
               total_computed_time=0.0001 # to ovoid division by zero, but we have to decide what to do with this repliation context (no displaying them or greyed out)

             aux_lrepl_client_time_stats[1]=total_computed_time # We assign the computed time to the aux_lrepl_client_time_stats, if it is 0 or if it is not

             # We are using dic_ctx_usage_time as the auxiliar context where we are putting all the information about each key, before adding it to list_ctx_usage_time
             dic_ctx_usage_time={}
             dic_ctx_usage_time={'key':'Total time spent by the replication context','value':total_computed_time,'unit': 'seconds'}
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time sending references. Problems with float operations and number of digits after the '.' I need to figure a better way. decimal module?
             # For making this inter DD OS version, we have coded the give_me_position_in_header_of Function
             # The problem is that between DD OS ASUPS, sometime the headers of the lrepl client time stats do not store the value for a key in the same positional column
             # therefore we need to obtain first in which position it is the right information, if we do not want to plot things that are not accurate.
             # if the function returns -1 is that they key has not being found
             # It is a good idea probably to assign a key to 0 if it has not being found

             position=self.give_me_position_in_header_of('send_refs')
             tsr_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={'key': 'Time sending references', 'value':tsr_percentage,'unit': '%' }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time sending segments
             position=self.give_me_position_in_header_of('send_segs')
             tss_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={'key': 'Time sending segments', 'value':tss_percentage, 'unit': '%' }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time receiving references
             position=self.give_me_position_in_header_of('recv_refs')
             trr_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time receiving references", "value": trr_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time waiting for references from destination
             position=self.give_me_position_in_header_of('recv_refs_sleep')
             twrd_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time waiting for references from destination", "value": twrd_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time waiting getting references
             position=self.give_me_position_in_header_of('get_refs')
             twgr_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time waiting getting references", "value": twgr_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time local reading segments
             position=self.give_me_position_in_header_of('read_segs')
             tlls_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time local reading segments", "value": tlls_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time sending small files
             position=self.give_me_position_in_header_of('send_small_file')
             tsmf_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time sending small files", "value": tsmf_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time sending sketches
             position=self.give_me_position_in_header_of('send_sketches')
             tse_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time sending sketches", "value": tse_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time receiving bases
             position=self.give_me_position_in_header_of('recv_bases')
             trb_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time receiving bases", "value": tse_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time reading bases
             position=self.give_me_position_in_header_of('read_bases')
             treadb_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time reading bases", "value": treadb_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time getting chunk info
             position=self.give_me_position_in_header_of('get_chunk_info')
             tgci_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time getting chunk info", "value": tgci_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             # Time unpacking chunks of info
             position=self.give_me_position_in_header_of('unpack_chunks')
             tupi_percentage=float(aux_lrepl_client_time_stats[position])*100/total_computed_time
             dic_ctx_usage_time={ "key": "Time unpacking chunks of info", "value": tupi_percentage, "unit": "%" }
             list_ctx_usage_time.append(dic_ctx_usage_time)
             dic_ctx_usage_time={}

             _log.debug("What list_ctx_usage_time contains:{}".format(list_ctx_usage_time))
              # TO DO We will have to create the graph here from the info contained in list_ctx_usage_time
              # We build the graph here

             graph=ReplicationContextPlot()

             save_name_path=app.config['STATIC_DIR_PATH']
             save_name="ctxplot"+"-"+graph.random_name(5)+".png" # We create a random name 5 characters long

             returned_graph=graph.plot_context(list_ctx_usage_time,os.path.join(save_name_path,save_name))

             if(returned_graph==os.path.join(save_name_path,save_name)): # We suceeded to create the graph
               _log.debug("We suceeded to create the graph named:{}".format(save_name))
             else:
               _log.debug("Seems that not all the columns required to plot the graph are there. Name of the graph:{}".format(save_name))


             _log.debug("Name of the graph:{}".format(save_name))

             dic_auxiliar_2={'graphImage': save_name}

             dic_auxiliar.update(dic_auxiliar_2)
             """
             # This is how it was originally pointing to a resource under frontend src
             #dic_auxiliar_2={'graphImage': 'assets/ctxgraph93808.png'}
             #dic_auxiliar.update(dic_auxiliar_2)
             """

             # END OF THE GRAPH, we keep adding what is remaining
             dic_auxiliar.update(dic_ctx_usage_time) # Method update of the dictionary dict.update(dict2) what it does it do add dict2´s key-values pair in to dict (like removing one nexted dictionary)
             dic_auxiliar['ctxUsageTime']=list_ctx_usage_time # And now we add the key 'ctxUsageTime'
             final_data_structure.append(dic_auxiliar) # And we add to the list resultado, which is the final data structure being processed


             _log.debug("THE FINAL DATA STRUCTURE BUILD AFTER CONTEXT ANALYSIS IS:{}".format(final_data_structure))
             _log.debug("WE HAVE FINISHED THE ANALYSIS OF %d REPLICATION CONTEXTS",len(final_data_structure))





         # lets generate a PDF Report

        """pdf_report=PDFHelper()
        report_name="./reports/ReplicationReportCtx-"+"2"+".pdf"
        pdf_report.GenerateReport(final_data_structure,2,report_name)

        report_name="./reports/ReplicationReportCtx-"+"4"+".pdf"
        pdf_report.GenerateReport(final_data_structure,4,report_name)
        report_name="./reports/ReplicationReportCtx-"+"6"+".pdf"
        pdf_report.GenerateReport(final_data_structure,6,report_name)
        report_name="./reports/ReplicationReportCtx-"+"8"+".pdf"
        pdf_report.GenerateReport(final_data_structure,8,report_name)
        report_name="./reports/ReplicationReportCtx-"+"9"+".pdf"
        pdf_report.GenerateReport(final_data_structure,9,report_name)
        report_name="./reports/ReplicationReportCtx-"+"15"+".pdf"
        pdf_report.GenerateReport(final_data_structure,15,report_name)
        report_name="./reports/ReplicationReportCtx-"+"15"+".pdf"
        pdf_report.GenerateReport(final_data_structure,15,report_name)
        """


        return(final_data_structure)
         # Just as a reference, this is the structure we need to end up having
