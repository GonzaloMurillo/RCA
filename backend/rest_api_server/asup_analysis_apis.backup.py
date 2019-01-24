#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request
from rest_api_server import app
import os
import random
from util import version, logger
import json
from dellemc.datadomain import DataDomain
from dellemc.replicationcontextplot import ReplicationContextPlot


_log = logger.get_logger(__name__)

# Globals - Move to ctxdoing class/object
asup_file_save_path = None
asup_auto_cores_location = None
asup_elysium_serial_number = None
selected_replication_contexts = None

ASUP_FILE_INPUT_METHODS = {
    'FILE_UPLOAD': 1,
    'AUTO_CORES_PATH': 2,
    'ELYSIUM_SERIAL_NUMBER': 3
    }
asup_file_input_method = None

# This is for autosupport being provided as an upload

@app.route("/api/asup/file", methods=['POST'])
def asup_file_upload():
    global asup_file_save_path, asup_file_input_method

    _log.info("ASUP file uploaded: %s", request.files)

    f = request.files['asup']
    asup_file_save_path = os.path.join(app.config['RUNTIME_WORKING_DIR'], f.filename)
    f.save(asup_file_save_path)
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['FILE_UPLOAD']
    _log.info('[asup_file_input_method=FILE_UPLOAD] ASUP file saved locally as: %s', asup_file_save_path)

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

# This is for autosupport being provided as a path to /auto/cores

@app.route("/api/asup/auto_cores_path", methods=['POST'])
def asup_file_auto_cores_path():
    global asup_auto_cores_location, asup_file_input_method

    data = json.loads(request.data)
    asup_auto_cores_location = data['auto_cores_path']
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH']
    _log.info('[asup_file_input_method=AUTO_CORES_PATH] ASUP file located at: %s', asup_auto_cores_location)

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

# This is for autosupport being provided from Elysium

@app.route("/api/asup/elysium_serial_number", methods=['POST'])
def asup_file_elysium_serial_number():
    global asup_elysium_serial_number, asup_file_input_method

    data = json.loads(request.data)
    asup_elysium_serial_number = data['elysium_serial_number']
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['ELYSIUM_SERIAL_NUMBER']
    _log.info('[asup_file_input_method=ELYSIUM_SERIAL_NUMBER] Serial Number: %s', asup_elysium_serial_number)

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

# Displaying just the source (and valid) replication context from the autosupport

@app.route("/api/asup/analysis/replication_contexts", methods=['GET', 'POST'])
def replication_contexts_list():
    global selected_replication_contexts, asup_file_input_method,dd # I do convert in global de dd object of class DataDomain

    _log.info(asup_file_input_method)

    # Backend for the upload method

    if(asup_file_input_method==1): #File has been uploaded

        _log.info(asup_file_save_path)
        asup_file_save_path_escaped=asup_file_save_path.encode("utf-8") # To remove issues with path in Windows
        _log.info(asup_file_save_path_escaped)
        dd=DataDomain(asup_file_save_path_escaped) # Most of the backend is done in the class DataDomain, we create an instance
    if request.method == 'GET':

        _log.info("START of the method to display the contexts of the autosuport that has being uploaded")
        repl_ctx_list = []
        _log.info("Replication Contexts frontend {}".format(dd.replication_contexts_frontend))
        for item in dd.replication_contexts_frontend: # In dd.replication_contexts_frontend, we have just the contexts displayed in the frontend, but we want to filter from them just to display source and valid replication contexts
            _log.info("Searching for just source replication contexts")
            if(dd.is_source_context(item['ctx'])):
                _log.info("The context{}, is a source replication context".format(item))
                # Here we should also add checkings if it is also a valid context like for example if there is lrepl client time stats for that context in the autosupport, because if there a lot of context no all of them are calculated
                # for now, we simply add to the list:get_repl_ctx_list
                _log.info("Adding the context number:{} to the list of source and valid replication contexts".format(item))
                repl_ctx_list.append(item)


        _log.info("Found %d source and valid replication contexts", len(repl_ctx_list))
        _log.info("List to jsonify {}".format(repl_ctx_list))
        _log.info("END of the method to display the contexts of the autosuport that has being uploaded")
        return (jsonify(repl_ctx_list),
                200,
                {'ContentType': 'application/json'})

    # Is this if we click backwards in the browser?
    elif request.method == 'POST':
        selected_replication_contexts = json.loads(request.data)


        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

# This is where the real analysis of the context happens
@app.route("/api/asup/analysis/replication_contexts/time_spent", methods=['GET'])
def analyze_replication_contexts():
    # Call ctxdoing to analyze selected replication contexts
      # 'data' is a list similar to that returned by ctxdoing.get_repl_ctx_list()
      # result = ctxdoing.analyze_repl_ctx(data)
      _log.info("START of the method to analyze the contexts provided")
      _log.info("The selected replication context that need analysis are:{}".format(selected_replication_contexts))
      resultado=[] # This is the final structure that we are going to build

      # We iterate between the selected replication contexts

      for itera_dict in selected_replication_contexts: # selected_replication_contexts is the info that comes from the selection context screen
          _log.info("itera dict:{}".format(itera_dict))

          dic_auxiliar={}
          dic_auxiliar['ctxDetails']=itera_dict # We add to the dic auxiliar the key {'ctxDetails'} that will contain the details of the context
          list_ctx_usage_time=[] # This list will contain the context lrepl client time stats values

          aux_lrepl_client_time_stats=[] # This list is going to content the lrepl client time stats of that particular context
          # Now we need to obtain the lrepl_client_time_stats for the context that we are analyzing. That info is already in the DataDomain object because the constructor does
          for i in range(1,len(dd.lrepl_client_time_stats)): # We start in 1, because dd,lrepl_client_time_stats[0], just contains the header
              searching_for="rctx://"+str(itera_dict['ctx'])
              _log.info("We are searching the Lrepl client time stats of context:{}".format(searching_for))

              if(dd.lrepl_client_time_stats[i][0]==searching_for): # We are searching for on one of the specific contexts selected for analysis
                  _log.info("We have foud the lrepl_client_time_stats of the context {}".format(searching_for))
                  # We found it, so we make the aux_lrepl_client_time_stats equal to the list that corresponds in the dd object
                  aux_lrepl_client_time_stats=dd.lrepl_client_time_stats[i]
                  # And we exit
                  break
          _log.info("The list aux_lrepl_client_time_stats for the contex:{} now contains{}".format(searching_for,aux_lrepl_client_time_stats))

          # We do the maths as we are using relative values instead of relying on the calculation coming in the autosupport
          sum=0
          for x in range(1,len(aux_lrepl_client_time_stats)):
              sum=sum+int(aux_lrepl_client_time_stats[x])

          _log.info("The total time spent by context {} is {} as calculated by adding together all the values".format(searching_for,sum))
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
          # The problem that makes this not compatible with versions <= 6.02 is that we use here the absolute field like in aux_lrepl_client_time_stats[2]
          # But not always, for example the Time Sending References would be the field 2, we would have to consult first the header dd.lrepl_client_time_stats[0]
          # to identify the position of each parameter
          tsr_percentage=float(aux_lrepl_client_time_stats[2])*100/total_computed_time
          dic_ctx_usage_time={'key': 'Time sending references', 'value':tsr_percentage,'unit': '%' }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time sending segments

          tss_percentage=float(aux_lrepl_client_time_stats[3])*100/total_computed_time
          dic_ctx_usage_time={'key': 'Time sending segments', 'value':tss_percentage, 'unit': '%' }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time receiving references
          trr_percentage=float(aux_lrepl_client_time_stats[4])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time receiving references", "value": trr_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time waiting for references from destination
          twrd_percentage=float(aux_lrepl_client_time_stats[5])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time waiting for references from destination", "value": twrd_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time waiting getting references
          twgr_percentage=float(aux_lrepl_client_time_stats[6])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time waiting getting references", "value": twgr_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time local reading segments
          tlls_percentage=float(aux_lrepl_client_time_stats[7])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time local reading segments", "value": tlls_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time sending small files
          tsmf_percentage=float(aux_lrepl_client_time_stats[8])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time sending small files", "value": tsmf_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time sending sketches
          tse_percentage=float(aux_lrepl_client_time_stats[9])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time sending sketches", "value": tse_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time receiving bases
          trb_percentage=float(aux_lrepl_client_time_stats[10])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time receiving bases", "value": tse_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time reading bases
          treadb_percentage=float(aux_lrepl_client_time_stats[11])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time reading bases", "value": treadb_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time getting chunk info
          tgci_percentage=float(aux_lrepl_client_time_stats[12])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time getting chunk info", "value": tgci_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          # Time unpacking chunks of info
          tupi_percentage=float(aux_lrepl_client_time_stats[13])*100/total_computed_time
          dic_ctx_usage_time={ "key": "Time unpacking chunks of info", "value": tupi_percentage, "unit": "%" }
          list_ctx_usage_time.append(dic_ctx_usage_time)
          dic_ctx_usage_time={}

          _log.info("What list_ctx_usage_time contains:{}".format(list_ctx_usage_time))
           # TO DO We will have to create the graph here from the info contained in list_ctx_usage_time
           # We build the graph here

          random_number=random.randint(1,100000)
          #save_name=os.path.join(app.config['RUNTIME_WORKING_DIR']+"\\graphs", "graficogonzalo"+str(random_number)+".png")
          save_name="C:\\DDTOOLS-master\\ctxdoing-master-branch\\ctxdoing\\frontend\\ctxdoing\\src\\assets\\graficogonzalo"+str(random_number)+".png"
          graph=ReplicationContextPlot(list_ctx_usage_time,save_name)
          nombre="graficogonzalo"+str(random_number)+".png"
          dic_auxiliar_2={'graphImage': nombre}
          dic_auxiliar.update(dic_auxiliar_2)
          """
          # Esto es como es originalmente
          #dic_auxiliar_2={'graphImage': 'assets/replicationgraph.png'}
          #dic_auxiliar.update(dic_auxiliar_2)
          # END OF THE GRAPH
          dic_auxiliar.update(dic_ctx_usage_time) # Method update of the dictionary dict.update(dict2) what it does it do add dict2´s key-values pair in to dict (like removing one nexted dictionary)
          dic_auxiliar['ctxUsageTime']=list_ctx_usage_time # And now we add the key 'ctxUsageTime'
          resultado.append(dic_auxiliar) # And we add to the list resultado, which is the final data structure being processed


          _log.info("THE FINAL DATA STRUCTURE BUILD AFTER CONTEXT ANALYSIS IS:{}".format(resultado))
          _log.info("WE HAVE FINISHED THE ANALYSIS OF %d REPLICATION CONTEXTS",len(resultado))
          # Just as a reference, this is the structure we need to end up having

         
            result = [
                {
                  'ctxDetails': {
                     'ctx': 1,
                     'source': {
                         'host': 'dd390gcsr01.nam.nsroot.net',
                         'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'#he quitado una coma
                         },
                     'destination': {
                         'host': 'dd390gcsr02.nam.nsroot.net',
                         'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'
                        }
                    },
                  # Save PNG generated by matplotlib in app.config['STATIC_DIR_PATH'] andgive it a UUID
                  # Then set this path to /static/img-uuid-here.png
                  'graphImage': 'assets/replicationgraph.png',
                  'ctxUsageTime': [
                    { "key": "Total time spent by the replication context", "value": "11362471", "unit": "seconds" },
                    { "key": "Time sending references", "value": "0.2", "unit": "%" },
                    { "key": "Time sending segments", "value": "1.5", "unit": "%" },
                    { "key": "Time receiving references", "value": "0.4", "unit": "%" },
                    { "key": "Time waiting for references from destination", "value": "1.4", "unit": "%" },
                    { "key": "Time waiting getting references", "value": "2.9", "unit": "%" },
                    { "key": "Time local reading segments", "value": "93.6", "unit": "%" },
                    { "key": "Time sending small files", "value": "0.0", "unit": "%" },
                    { "key": "Time sending sketches", "value": "0.0", "unit": "%" },
                    { "key": "Time receiving bases", "value": "0.0", "unit": "%" },
                    { "key": "Time reading bases", "value": "0.0", "unit": "%" },
                    { "key": "Time getting chunk info", "value": "0.0", "unit": "%" },
                    { "key": "Time unpacking chunks of info", "value": "0.0", "unit": "%" }
                  ]
                },
                'ctxDetails': {
                   'ctx': 2,
                   'source': {
                       'host': 'dd390gcsr01.nam.nsroot.net',
                       'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'#he quitado una coma
                       },
                   'destination': {
                       'host': 'dd390gcsr02.nam.nsroot.net',
                       'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'
                      }
                  },
                # Save PNG generated by matplotlib in app.config['STATIC_DIR_PATH'] andgive it a UUID
                # Then set this path to /static/img-uuid-here.png
                'graphImage': 'assets/replicationgraph.png',
                'ctxUsageTime': [
                  { "key": "Total time spent by the replication context", "value": "11362471", "unit": "seconds" },
                  { "key": "Time sending references", "value": "0.2", "unit": "%" },
                  { "key": "Time sending segments", "value": "1.5", "unit": "%" },
                  { "key": "Time receiving references", "value": "0.4", "unit": "%" },
                  { "key": "Time waiting for references from destination", "value": "1.4", "unit": "%" },
                  { "key": "Time waiting getting references", "value": "2.9", "unit": "%" },
                  { "key": "Time local reading segments", "value": "93.6", "unit": "%" },
                  { "key": "Time sending small files", "value": "0.0", "unit": "%" },
                  { "key": "Time sending sketches", "value": "0.0", "unit": "%" },
                  { "key": "Time receiving bases", "value": "0.0", "unit": "%" },
                  { "key": "Time reading bases", "value": "0.0", "unit": "%" },
                  { "key": "Time getting chunk info", "value": "0.0", "unit": "%" },
                  { "key": "Time unpacking chunks of info", "value": "0.0", "unit": "%" }
                ]
              }


            ]
      """


      return (jsonify(resultado),
              200,
              {'ContentType': 'application/json'})
