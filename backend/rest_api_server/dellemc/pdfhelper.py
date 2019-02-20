from fpdf import FPDF
from util import logger
_log = logger.get_logger(__name__)

### This is a class for helping with the creation of the PDF Report. It uses the library pypfdf and hence it needs to be installed.

class PDFHelper():
    # Class constructor
    def __init__(self):
        return

# This is a function method to calculate the 2 operations that are taking longer in the replication stats, so we can paint it differently in the report

    def CalculateMax(self,ctx_list_of_dic_info,context_number):

        print("CalculateMax context list of dif {}".format(ctx_list_of_dic_info))
        values_to_compare=[]
        for iter_dic in ctx_list_of_dic_info:
            print("iter_dic {}".format(iter_dic))
            if iter_dic['ctxDetails']['ctx']==context_number:
                print("I have find information for the context searched {}".format(context_number))
                for element in iter_dic:
                    if element=='ctxUsageTime':
                        print("coincide")
                        for sub_item in iter_dic['ctxUsageTime']:
                            if(sub_item['key']=='Time sending references'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time sending segments'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time receiving references'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time waiting for references from destination'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time waiting getting references'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time local reading segments'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time sending small files'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time sending sketches'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time receiving bases'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time reading bases'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time getting chunk info'):
                                values_to_compare.append(sub_item['value'])
                            if(sub_item['key']=='Time unpacking chunks of info'):
                                values_to_compare.append(sub_item['value'])

                # We sort the list, to return the 2 bigger values.
                values_to_compare.sort(reverse=True)
                # I double check to avoid
                _log.info("Content of values_to_compare:{}".format(values_to_compare))
                return(values_to_compare[0],values_to_compare[1])
            # Method that generates the report itself

    def GenerateReport(self,ctx_list_of_dic_info,context_number,report_file_name): #ctx_dic_info is a dictionary structure with information about everything that needs to be added in the report

        _log.warning("What arrives to the method GenerateReport {}".format(ctx_list_of_dic_info))
        _log.warning("I have been requested to generate a report for context {}".format(context_number))
        maximum,second=self.CalculateMax(ctx_list_of_dic_info,context_number)
        maximum="{:.2f}".format(maximum)
        second="{:.2f}".format(second)
        for iter_dic in ctx_list_of_dic_info:
            _log.info("Comparying:{} with:{}".format(iter_dic['ctxDetails']['ctx'],int(context_number)))
            _log.info("Type {} and {}".format(type(iter_dic['ctxDetails']['ctx']),type(context_number)))

            if iter_dic['ctxDetails']['ctx']==context_number:
                _log.info("I have been requested to generate a report for {}".format(context_number))
                # Now I do have to generate the report file of iter_dic
                pdf_report = FPDF(orientation = 'P', unit = 'mm', format='A4')
                pdf_report.set_font('Arial', 'B', 15)
                report_title="REPLICATION CONTEXT ANALYZER REPORT"
                report_line_1="REPORT FOR CONTEXT://{}".format(iter_dic['ctxDetails']['ctx'])
                report_line_2="FROM://{}{} TO://{}{}".format(iter_dic['ctxDetails']['source']['host'],iter_dic['ctxDetails']['source']['mtree'],iter_dic['ctxDetails']['destination']['host'],iter_dic['ctxDetails']['destination']['mtree'])
                pdf_report.add_page()
                # Logo

                pdf_report.rect(x= 10, y= 10, w= 198, h= 55, style = '')
                pdf_report.image('DellEMCLogo.png',x=12,y=11,w=100,type="png")
                pdf_report.set_y(pdf_report.get_y()+20)
                pdf_report.set_text_color(0,118,206)
                pdf_report.set_font('Arial', 'B', 20)
                pdf_report.cell(60, 10, report_title, 0, 1)
                pdf_report.set_text_color(0,0,0)

                pdf_report.set_font('Arial', 'B', 8)
                pdf_report.cell(60, 10, report_line_1, 0, 1)
                pdf_report.set_font('Arial', 'B', 8)
                pdf_report.cell(60, 10, report_line_2, 0, 2)
                posy_graph=pdf_report.get_y()+7
                graph_file="./static/"+iter_dic['graphImage']
                pdf_report.image(graph_file,x=10,y=posy_graph,w=120,type="png")
                pdf_report.set_y(posy_graph)
                # Box around the logo
                pdf_report.rect(x= 10, y=posy_graph, w= 198, h= 120.5, style = '')

                pdf_report.set_y(pdf_report.get_y()+85)

                for element in iter_dic:
                    if element=='ctxUsageTime':
                        y=posy_graph
                        pdf_report.set_y(y)
                        pdf_report.set_x(122)
                        print_header=True
                        for sub_element in iter_dic['ctxUsageTime']:
                            # For printing the header of the table
                            if print_header:
                                pdf_report.cell(w=86,h=10,txt="REPLICATION OPERATION STATS",align="C",border=1,ln=1)
                                pdf_report.set_x(122)
                                print_header=False

                            report_line="{}: {:.2f} {}".format(sub_element['key'],sub_element['value'],sub_element['unit'])
                            pdf_report.set_font('Arial', 'B', 7)
                            value_limited="{:.2f}".format(sub_element['value'])
                            print "comparando {} con {}".format(str(value_limited),str(maximum))

                            # If it is the maximum value, we paint it red
                            if str(value_limited.strip())==str(maximum.strip()):
                                    _log.info("Filling it in red")
                                    pdf_report.set_fill_color(255,0,0)
                                    pdf_report.cell(w=86,h=8.5,txt=report_line,border=1,fill=True,ln=1)
                                    pdf_report.set_fill_color(0,0,0)

                            # If it is the second after the maximum, we paint it yellow
                            elif str(value_limited.strip())==str(second.strip()):
                                    pdf_report.set_fill_color(255,255,0)
                                    pdf_report.cell(w=86,h=8.5,txt=report_line,border=1,fill=True,ln=1)
                                    pdf_report.set_fill_color(0,0,0)
                            else:
                                # If it is not the max or the second, we paint the cell with no fill
                                pdf_report.cell(w=86,h=8.5,txt=report_line,border=1,ln=1)
                            pdf_report.set_x(122)

                # Saving the report
                pdf_report.output(report_file_name, 'F')
