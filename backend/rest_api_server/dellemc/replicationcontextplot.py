from util import version, logger
import matplotlib.pyplot as plt
import random
_log = logger.get_logger(__name__)
class ReplicationContextPlot():

  def __init__(self):
      return
  # This funcion plots a replication context from the information received in lrepl_client_time_stats and save it to the file received in the parameter save_name
  def plot_context(self,lrepl_client_time_stats,save_name):
      self.lrepl_client_time_stats=lrepl_client_time_stats # lrepl_client_time_stats is a list of dictionaries
      self.save_name=save_name
      _log.info("Save name:{}".format(self.save_name))
      _log.info("Lrep client time stats received by the class ReplicationContextPlot {}".format(lrepl_client_time_stats))

      num_keys=0 # Security mechanism to ensure that we have all the keys:
      for i,iterator_list in enumerate(lrepl_client_time_stats):
          _log.info("List number:{}".format(i))
          _log.info("key:{}|value:{}".format(iterator_list['key'],iterator_list['value']))

          if ('key' in iterator_list and iterator_list['key']=='Time sending references'):
              send_refs_percentage=iterator_list['value']
              num_keys+=1
          if ('key' in iterator_list and iterator_list['key']=='Time sending segments'):
              send_segs_percentage=iterator_list['value']
              num_keys+=1
          if ('key' in iterator_list and iterator_list['key']=='Time receiving references'):
              recv_refs_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time waiting for references from destination'):
              recv_refs_sleep_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time waiting getting references'):
              get_refs_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time local reading segments'):
              read_segs_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time sending small files'):
              send_small_file_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time sending sketches'):
              send_sketches_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time receiving bases'):
              recv_bases_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time reading bases'):
              read_bases_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time getting chunk info'):
              get_chunk_info_percentage=iterator_list['value']
              num_keys+=1
          if('key' in iterator_list and iterator_list['key']=='Time unpacking chunks of info'):
              unpack_chunks_percentage=iterator_list['value']
              num_keys+=1

      _log.info("Num of keys:{}".format(num_keys))
      if(num_keys!=12): # If we do not have all the keys, we do not plot a graph, just return an image to indicate that we failed to plot it.
          return "nograph.jpg"


      _log.info("send_refs_percentage:{}".format(send_refs_percentage))
      labels = ['Sending refs:'+format(send_refs_percentage,'.1f')+"%", 'Sending segs:'+format(send_segs_percentage,'.1f')+"%",'Receiving refs:'+format(recv_refs_percentage,'.1f')+"%",
    'Waiting refs:'+format(recv_refs_sleep_percentage,'.1f')+"%",'Getting refs:'+format(get_refs_percentage,'.1f')+"%",
    'Local read segs:'+format(read_segs_percentage,'.1f')+"%",'Sending small files:'+format(send_small_file_percentage,'.1f')+"%",'Sending sketches:'+format(send_sketches_percentage,'.1f')+"%",
    'Receiving bases:'+format(recv_bases_percentage,'.1f')+"%",'Reading bases:'+format(read_bases_percentage,'.1f')+"%",'Getting chunk info:'+format(get_chunk_info_percentage,'.1f')+"%",
    'Unpack chunks:'+format(unpack_chunks_percentage,'.1f')+"%"]

      sizes = [format(send_refs_percentage,'.1f'),format(send_segs_percentage,'.1f'),format(recv_refs_percentage,'.1f'),format(recv_refs_sleep_percentage,'.1f'),format(get_refs_percentage,'.1f'),format(read_segs_percentage,'.1f'),format(send_small_file_percentage,'.1f'),format(send_sketches_percentage,'.1f'),format(recv_bases_percentage,'.1f'),format(read_bases_percentage,'.1f'),format(get_chunk_info_percentage,'.1f'),format(unpack_chunks_percentage,'.1f')]
      max_value_found = max(sizes)
      pos = sizes.index(max_value_found)
      tuple0 = (0,)
      tuple1 = (0.5,) # This defines how much separation we want from the non exploded part of the graph
      explode = tuple()

    # We 'explode' in the graph the greatest value, bt we need to find it first and build the explode tuple
      for i in range(0, 12):
          if (i == pos):
              explode = explode + tuple1
          else:
              explode = explode + tuple0
      #print(plt.style.available)
      #plt.style.use('fivethirtyeight')

      fig1, ax1 = plt.subplots()

      fig1.set_figheight(6)
      fig1.set_figwidth(6)
      ax1.pie(sizes, explode=explode, startangle=90)
      first_legend = plt.legend(labels, loc=0, fancybox=True,framealpha=0.1) # The legend explaining what each value means
      ax = plt.gca().add_artist(first_legend)
      ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
      title = 'TIME SPENT BY EACH REPLICATION OPERATION'
      ax1.set_title(title, fontsize=15)

      _log.info("We are going to save the graph:{}".format(self.save_name))
      graph_saved=self.save_name
      plt.savefig(graph_saved,facecolor="#fafafa") # We save the graph
      return (graph_saved)

  def random_name(self,lenght_of_name):

      alphabet="abcdefghijklmnopqrstuvwyz"
      alphabet2=alphabet.upper()
      nums="0123456789"
      alphabet=alphabet+alphabet2+nums
      random_name=[]
      print("The alphabet {}".format(alphabet))

      for i in range(0,lenght_of_name):
          random_number=random.randint(0,len(alphabet)-1)
          _log.info("the random number:{}".format(random_number))
          random_name.append(alphabet[random_number])


      return "".join(map(str,random_name))
