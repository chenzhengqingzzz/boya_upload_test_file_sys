# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 10:22:23 2022

@author: LZJ
"""

import os
import re
from tkinter import filedialog
import copy
import tkinter as tk
import pandas as pd
import pandas.io.formats.excel
from multiprocessing import Process


def get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension

def get_filePath_list(raw_path,file_list = []):
    for lists in os.listdir(raw_path):
        path = os.path.join(raw_path, lists)
        if os.path.isdir(path):
            get_filePath_list(path,file_list)
        elif path.endswith('.txt'):
            file_list.append(path)
    return file_list

def get_file_data(file_path,testname2):
    global SENSE, EQ, vcc_list
    testname = ''
    DATAlist = {}
    rows_list = {}
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        searchObj = re.match(r".*Failing.*, Dut (?P<dut>.*) Iref = (?P<rdv>.*) uA, tv = (?P<tv>.*) ns, (?P<vcc>.*) V, (?P<MHz>.*) MHz, (?P<result>.*)!!.*", line)
        if not searchObj:
            if 'test name' in line:
                if testname2 != '':
                    testname = testname2
                else:
                    searchObj = re.match(r".*test name: (?P<testname>.*_EQ.*=(?P<EQ>.*)_SE.*=(?P<SE>.*)) start.*", line)
                    testname = searchObj['testname']
                    testname = testname.replace('EQ=%d' % int(searchObj['EQ']), 'EQ=%.2fns' % EQ[int(searchObj['EQ'])])
                    testname = testname.replace('SE=%d' % int(searchObj['SE']), 'SE=%.2fns' % SENSE[int(searchObj['SE'])])
                if testname not in DATAlist:
                    DATAlist.update({testname:{}})
                    rows_list.update({testname:[]})
        else:
            if testname == '': 
                testname = testname2
                if testname not in DATAlist:
                    DATAlist.update({testname:{}})
                    rows_list.update({testname:[]})
            dut = searchObj['dut']
            rdv = searchObj['rdv']
            # tv = searchObj['tv'] + 'ns'
            vcc = searchObj['vcc'] + 'V'
            MHz = str(int(float(searchObj['MHz']))) + 'MHz'
            result = searchObj['result']
            if dut not in DATAlist[testname]:
                DATAlist[testname].update({dut:{}})
            if rdv not in DATAlist[testname][dut]:
                DATAlist[testname][dut].update({rdv:{'shmoo':{},'FreqMAXList':{}}})
            if vcc not in DATAlist[testname][dut][rdv]['shmoo']:
                DATAlist[testname][dut][rdv]['shmoo'].update({vcc:[]})
                DATAlist[testname][dut][rdv]['FreqMAXList'].update({vcc:'MAX'})
                if float(vcc.replace('V','')) not in vcc_list:
                    vcc_list.append(float(vcc.replace('V','')))
            if MHz not in rows_list[testname]:
                rows_list[testname].append(MHz)
            if len(DATAlist[testname][dut][rdv]['shmoo'][vcc]) - rows_list[testname].index(MHz):
                DATAlist[testname][dut][rdv]['shmoo'][vcc][rows_list[testname].index(MHz)] = result
            else:
                DATAlist[testname][dut][rdv]['shmoo'][vcc].append(result)
            if  DATAlist[testname][dut][rdv]['FreqMAXList'][vcc] != 'MAX' and rows_list[testname].index(MHz) == 0:
                DATAlist[testname][dut][rdv]['FreqMAXList'][vcc] = 'MAX'
            if 'FAIL' in DATAlist[testname][dut][rdv]['shmoo'][vcc]:
                if DATAlist[testname][dut][rdv]['shmoo'][vcc].index('FAIL'):
                    MAXFreq = float(rows_list[testname][DATAlist[testname][dut][rdv]['shmoo'][vcc].index('FAIL')-1].replace('MHz',''))
                else:
                    MAXFreq = 0
                DATAlist[testname][dut][rdv]['FreqMAXList'][vcc] = MAXFreq
            else:
                DATAlist[testname][dut][rdv]['FreqMAXList'][vcc] = float(rows_list[testname][-1].replace('MHz',''))
    return DATAlist,rows_list

def combine_DATAlist(DATAlist1,DATAlist2):
    for testname in DATAlist2:
        if testname in DATAlist1:
            for dut in DATAlist2[testname]:
                if dut in DATAlist1[testname]:
                    new_dut = str(int(list(DATAlist1[testname].keys())[-1]) + 1)
                else:
                    new_dut = dut
                DATAlist1[testname].update({new_dut:DATAlist2[testname][dut]})
        else:
            DATAlist1.update({testname:DATAlist2[testname]})
    return DATAlist1

def convert_to_string(n):
    chars = ['%c'%i for i in range(65,91)]
    b = ''
    s = n // 26
    y = n % 26
    if 0<s<=26:
        b = chars[s-1] + chars[y]
    elif s==0:
        b = chars[y]
    else:
        b = convert_to_string(s-1) + chars[y]
    return b

def set_excel_style(writer,sheet_name,startrow,startcol,endrow,endcol,dut,printlist):
    worksheets = writer.sheets
    worksheet = worksheets[sheet_name]
    #worksheet.hide_gridlines(option=2)
    workbook = writer.book
    format1 = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','font_size': 36,'text_wrap':0})
    red_format = workbook.add_format({'bg_color':'FFC7CE','align': 'center','valign': 'vcenter'})
    green_format = workbook.add_format({'bg_color':'C6EFCE','align': 'center','valign': 'vcenter'})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+3)+':'+convert_to_string(endcol)+str(endrow),
                                 {'type': 'text','criteria': 'containing','value': 'PASS','format': green_format})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+3)+':'+convert_to_string(endcol)+str(endrow),
                                 {'type': 'text','criteria': 'containing','value': 'FAIL','format': red_format})
    worksheet.write(startrow + 0, startcol, printlist[0])
    #worksheet.write(startrow + 1, startcol, '(%suA)'%printlist[1])
    if startcol==2:
        worksheet.write(startrow + 1, startcol-1, printlist[1], format1)
    worksheet.merge_range(startrow + 1, startcol, startrow + 1, endcol-1, '%.3fuA'%float(printlist[2]), format1)
    worksheet.set_column('A:B',16)
    worksheet.freeze_panes(0, 2)
    
def PrintMargin(ExcelWrite, Marginlist, vcc_list):
    row = 0
    col = 0
    workbook = ExcelWrite.book
    format1 = workbook.add_format({'bold': True, 'valign': 'vcenter', 'font_size': 14, 'text_wrap': 0})
    df = pd.DataFrame()
    df.to_excel(ExcelWrite, sheet_name='Margin_list')
    worksheets = ExcelWrite.sheets
    worksheet = worksheets['Margin_list']
    worksheet.write(row, col, 'VCC=(%.1f-%.1f)V'%(min(vcc_list),max(vcc_list)), format1)
    #worksheet.write(row + 1, col, 'Normal Freq=(10~56)MHz;Dual Freq=(10~60)MHz;Quad Freq=(10~60)MHz', format1)
    row += 2
    MAX_col = max({len(Marginlist[testname][dut]) for testname in Marginlist for dut in Marginlist[testname]})
    for testname in Marginlist:
        for dut in Marginlist[testname]:
            worksheet.write(row + int(dut), col + 0, testname)
            worksheet.write(row + int(dut), col + 1, 'Dut ' + dut)
            for j, Iref in enumerate(sorted(Marginlist[testname][dut], key=lambda x: float(x))):
                worksheet.write(row + int(dut), col + 2 + j, '%suA' % Iref)
            if Marginlist[testname][dut] != []:
                margin = '%.3fuA' % (float(max(Marginlist[testname][dut])) - float(min(Marginlist[testname][dut])))
            else:
                margin = 'NO_MARGIN'
            worksheet.write(row + int(dut), col + MAX_col + 4, margin)
        row += len(Marginlist[testname]) + 1
    worksheet.set_column('A:A', 48)
    worksheet.set_column('B:B', 6)

def PrintSummary(ExcelWrite, Marginlist, vcc_list):
    row = 0
    col = 0
    workbook = ExcelWrite.book
    format0 = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'text_wrap': 1})
    format1 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bg_color':'B8CCE4', 'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 1})
    format2 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bold': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 0, 'num_format': '0.000'})
    format3 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bg_color':'DCE6F1', 'bold': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 0, 'num_format': '0.000'})
    format4 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bg_color':'8DB4E2', 'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 0, 'num_format': '0.000'})
    format5 = workbook.add_format({'bg_color':'0070C0', 'bold': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 0})
    format6 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bold': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'underline': 1, 'font_color':'0000FF'})
    format7 = workbook.add_format({'border': 1, 'border_color':'4F81BD', 'bg_color':'DCE6F1', 'bold': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'underline': 1, 'font_color':'0000FF'})
    df = pd.DataFrame()
    df.to_excel(ExcelWrite, sheet_name='Summary')
    worksheets = ExcelWrite.sheets
    worksheet = worksheets['Summary']
    for testname in Marginlist:
        worksheet.merge_range(row, col, row, col + 4, testname, format0)
        worksheet.write(row + 1, col, '', format2)
        worksheet.write(row + 1, col + 1, '', format2)
        worksheet.write(row + 1, col + 2, '%.1f-%.1fV pgm'%(min(vcc_list),max(vcc_list)), format1)
        worksheet.write(row + 1, col + 3, '%.1f-%.1fV erase'%(min(vcc_list),max(vcc_list)), format1)
        worksheet.write(row + 1, col + 4, '%.1f-%.1fV margin'%(min(vcc_list),max(vcc_list)), format1)
        worksheet.merge_range(row + 2, col, row + len(Marginlist[testname]) + 2, col, testname, format1)
        row += 2
        for dut in Marginlist[testname]:
            if Marginlist[testname][dut]==[]:
                Margin_PGM = 0
                Margin_ER = 0
                Margin_val = 0
            else:
                Margin_PGM = float(min(Marginlist[testname][dut]))
                Margin_ER = float(max(Marginlist[testname][dut]))
                Margin_val = Margin_ER - Margin_PGM
            if int(dut)%2:
                format_print = format3
                worksheet.write(row + int(dut), col + 1, 'DUT' + dut, format7)
            else:
                format_print = format2
                worksheet.write(row + int(dut), col + 1, 'DUT' + dut, format6)
            worksheet.write(row + int(dut), col + 2, Margin_PGM, format_print)
            worksheet.write(row + int(dut), col + 3, Margin_ER, format_print)
            worksheet.write(row + int(dut), col + 4, Margin_val, format_print)
        worksheet.write(row + len(Marginlist[testname]), col + 1, 'AVERAGE', format4)
        worksheet.write(row + len(Marginlist[testname]), col + 2, '=AVERAGE(%s:%s)'%(convert_to_string(col + 2)+str(row + 1),convert_to_string(col + 2)+str(row + len(Marginlist[testname]))), format4)
        worksheet.write(row + len(Marginlist[testname]), col + 3, '=AVERAGE(%s:%s)'%(convert_to_string(col + 3)+str(row + 1),convert_to_string(col + 3)+str(row + len(Marginlist[testname]))), format4)
        worksheet.write(row + len(Marginlist[testname]), col + 4, '=AVERAGE(%s:%s)'%(convert_to_string(col + 4)+str(row + 1),convert_to_string(col + 4)+str(row + len(Marginlist[testname]))), format4)
        row += len(Marginlist[testname]) + 1
        for i in range(5):
            worksheet.write(row, col + i, '', format5)
        row += 1
    worksheet.set_column('A:A', 18)
    worksheet.set_column('B:B', 9)
    worksheet.set_column('C:E', 18)
    
def data_to_excel(dest_filename,DATAlist,rows,vcc_list):
    err = 20.0
    Freqlimit = 60.0
    Marginlist = {}
    ExcelWrite = pd.ExcelWriter(dest_filename)
    printlist = [0 for i in range(5)]
    # for i,testname in enumerate(DATAlist):
    for testname in DATAlist:
        printlist[0] = testname
        # for dut in DATAlist[testname]:
        for i, dut in enumerate(DATAlist[testname]):
            printlist[1] = 'Dut' + dut
            MAXFreq_cmp = {vcc:max(max(map(lambda x: DATAlist[testname][dut][x]['FreqMAXList'][vcc],DATAlist[testname][dut]))-err,Freqlimit) \
                            for vcc in list(DATAlist[testname][dut][list(DATAlist[testname][dut])[0]]['FreqMAXList'])}
            if testname not in Marginlist:
                Marginlist.update({testname:{}})
            if dut not in Marginlist:
                Marginlist[testname].update({dut:[]})
            for j,iref in enumerate(sorted(DATAlist[testname][dut], key=lambda x: float(x))):
                if all(DATAlist[testname][dut][iref]['FreqMAXList'][vcc] > MAXFreq_cmp[vcc] \
                       for vcc in DATAlist[testname][dut][iref]['FreqMAXList']):
                    Marginlist[testname][dut].append(float(iref))
                printlist[2] = iref
                df = pd.DataFrame(DATAlist[testname][dut][iref]['shmoo'])
                df.index = rows[testname]
                if not j:
                    # df.to_excel(ExcelWrite, sheet_name = printlist[1], startrow = i * (df.shape[0] + 4) + 3,
                    #             startcol= j * (df.shape[1]) + 1, index = True, header = True)
                    df.to_excel(ExcelWrite, sheet_name = testname[-31:], startrow = i * (df.shape[0] + 4) + 3,
                                startcol= j * (df.shape[1]) + 1, index = True, header = True)
                else:
                    # df.to_excel(ExcelWrite, sheet_name = printlist[1], startrow = i * (df.shape[0] + 4) + 3,
                    #             startcol= j * (df.shape[1]) + 2, index = False, header = True)
                    df.to_excel(ExcelWrite, sheet_name = testname[-31:], startrow = i * (df.shape[0] + 4) + 3,
                                startcol= j * (df.shape[1]) + 2, index = False, header = True)
                start_row = i * (df.shape[0] + 4) + 1
                start_col = j * (df.shape[1]) + 2
                end_row = start_row + df.shape[0] + 1 + 4
                end_col = start_col + df.shape[1]
                # set_excel_style(ExcelWrite, printlist[1], start_row, start_col, end_row, end_col, dut, printlist)
                set_excel_style(ExcelWrite, testname[-31:], start_row, start_col, end_row, end_col, dut, printlist)
    PrintMargin(ExcelWrite, Marginlist, vcc_list)
    PrintSummary(ExcelWrite, Marginlist, vcc_list)
    ExcelWrite.save()

if __name__ == '__main__':
    DATAlist_tmp = {}
    FAILflie_list = []
    rows_list = {}
    threads = []
    process_list = []
    vcc_list = []
    EQ = [4.000, 4.000, 4.900, 4.900 ,5.800, 5.800, 6.700, 6.700, 7.600, 7.600, 8.500, 8.500, 9.400, 9.400, 10.300, 10.300]
    root = tk.Tk()
    root.withdraw()
    #file_path = filedialog.askopenfilename()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    #file_list.sort(key= lambda x:int(re.findall(r"_j=([\d]{1,})_s[\d]{1,}\.txt", x)[0]))
    flielist_cmp = copy.deepcopy(file_list)
    for file in file_list:
        try:
            print(file)
            raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file)
            testname = shotname.replace(re.findall(r"(_s[\d]{1,})", file)[0],'')
            testname = testname.replace('quadio_read_by32byte','qio_by32')
            if 'RC' in testname:
                SENSE = [14.500, 14.500, 16.800, 16.800, 19.100, 19.100, 21.400, 21.400, 23.700, 23.700, 25.000, 25.000, 27.300, 27.300, 30.500, 30.500]
            elif 'CLK' in testname:
                SENSE = [11.500, 11.500, 13.000, 13.000, 14.500, 14.500, 16.000, 16.000, 17.500, 17.500, 19.000, 19.000, 20.500, 20.500, 22.000, 22.000]
            searchObj = re.match(r".*_EQ=(?P<EQ>[0-9]{1,})_SE=(?P<SE>[0-9]{1,})", testname)
            if searchObj:
                testname = testname.replace('EQ=%d' % int(searchObj['EQ']), 'EQ=%.2fns' % EQ[int(searchObj['EQ'])])
                testname = testname.replace('SE=%d' % int(searchObj['SE']), 'SE=%.2fns' % SENSE[int(searchObj['SE'])])
            DATAlist,rows_list_tmp = get_file_data(file,testname)
            DATAlist_tmp = combine_DATAlist(DATAlist_tmp,DATAlist)
            rows_list.update(rows_list_tmp)
        except:
            FAILflie_list.append(file)
        flielist_cmp.remove(file)
        if all(raw_filepath not in file_cmp for file_cmp in flielist_cmp):
            pandas.io.formats.excel.header_style = None
            for thread in threads:
                thread.join()
            try:
                shotname = shotname.replace(re.findall(r"(_s[\d]{1,})", file)[0],'')
            finally:
                dest_filename = raw_filepath + r'/' + shotname + r'.xlsx'
            # data_to_excel(dest_filename,DATAlist_tmp,rows_list,vcc_list)
            process = Process(target = data_to_excel,args=(dest_filename,DATAlist_tmp,rows_list,vcc_list,))
            process_list.append(process)
            process.start()
            DATAlist_tmp = {}
    for process in process_list:
        process.join()
    print('FAIL_list=' + str(FAILflie_list))

