# -*- coding: utf-8 -*-
"""
Created on Tue May 11 19:17:38 2021

@author: LZJ
"""

import os
import re
from tkinter import filedialog
import copy
import tkinter as tk
import pandas as pd
import pandas.io.formats.excel

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

def get_file_data(file_path,testname):
    DATAlist = {}
    Ireflist = {}
    Marginlist_tmp = {}
    Marginlist = {}
    rows = []
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        #* Failing DUTs 0x0, Dut 0 Iref = 2.238 uA, tv = 11.00 ns, 1.60 V, 10.00 MHz, PASS!!*
        searchObj = re.match(r".*Failing.*, Dut (.*) Iref = (.*) uA, tv = (.*) ns, (.*) V, (.*) MHz, (.*)!!", line)
        if not searchObj:
            #DEBUG Iref 0,1,0,0,0
            #searchObj = re.match(r"DEBUG (.*) (.*)", line)
            searchObj = re.match(r"(.*) = (.*)", line)
            if searchObj:
                if searchObj.group(1) == 'PRECHG':
                    PRECHG = searchObj.group(2)
                    if PRECHG not in DATAlist:
                        DATAlist.update({PRECHG:{}})
                        Ireflist.update({PRECHG:{}})
                        Marginlist.update({PRECHG:{}})
                        Marginlist_tmp.update({PRECHG:{}})
                elif searchObj.group(1) == 'EQLT':
                    EQLT = searchObj.group(2)
                    #EQLT = '0,1,1,1'
                    if EQLT not in DATAlist[PRECHG]:
                        DATAlist[PRECHG].update({EQLT:{}})
                        Ireflist[PRECHG].update({EQLT:{}})
                        Marginlist[PRECHG].update({EQLT:{}})
                        Marginlist_tmp[PRECHG].update({EQLT:{}})
                elif searchObj.group(1) == 'iref':
                    iref = searchObj.group(2)
                    if iref not in DATAlist[PRECHG][EQLT]:
                        DATAlist[PRECHG][EQLT].update({iref:{}})
                        Ireflist[PRECHG][EQLT].update({iref:{}})
                        Marginlist_tmp[PRECHG][EQLT].update({iref:{}})
        else:
            dut = searchObj.group(1)
            Iref = searchObj.group(2)
            #tv = searchObj.group(3) + 'ns'
            vcc = searchObj.group(4) + 'V'
            MHz = str(int(float(searchObj.group(5)))) + 'MHz'
            result = searchObj.group(6)
            if dut not in DATAlist[PRECHG][EQLT][iref]:
                DATAlist[PRECHG][EQLT][iref].update({dut:{}})
                Ireflist[PRECHG][EQLT][iref].update({dut:{}})
                Marginlist_tmp[PRECHG][EQLT][iref].update({dut:{}})
                Marginlist_tmp[PRECHG][EQLT][iref][dut] = 0
            if dut not in Marginlist[PRECHG][EQLT]:
                Marginlist[PRECHG][EQLT].update({dut:[]})
            if vcc not in DATAlist[PRECHG][EQLT][iref][dut]:
                DATAlist[PRECHG][EQLT][iref][dut].update({vcc:[]})
            if MHz not in rows:
                rows.append(MHz)
            Ireflist[PRECHG][EQLT][iref][dut] = Iref
            DATAlist[PRECHG][EQLT][iref][dut][vcc].append(result)
            #if ("normal" in testname) and ("32byte" not in testname):
            if "normal" in testname:
                vcc_min = 1.6
                freq_max = 10#80#45#10#50#10#55
                vcc_min2 = 2.2#2.3
                freq_max2 = 10#100#50#10#50#10#65
                cmp_cnt = 11#197#95#11#99#11#124
            elif "quad" in testname:
                vcc_min = 1.6#1.7#1.6#1.8
                freq_max = 80#80#10#75#10#70#80#80#90
                vcc_min2 = 3.0#1.8#1.7#1.6#1.8
                freq_max2 = 100#100#10#115#10#80#80#80#90
                cmp_cnt = 181#197#11#234#11#157#792#330#164
            elif "dual" in testname:
                vcc_min = 1.6#1.7#1.6#1.8
                freq_max = 90#80#10#80#10#70#80#80#90
                vcc_min2 = 2.4#1.8#1.7#1.6#1.8
                freq_max2 = 110#100#10#115#10#80#80#80#90
                cmp_cnt = 215#197#11#235#11#157#792#330#164
            else:
                vcc_min = 1.6
                freq_max = 50#115#10#115
                vcc_min2 = 2.0
                freq_max2 = 50#115#10#115
                cmp_cnt = 1#242#11#242
            if (float(vcc.replace('V','')) <= 3.8) and (((float(vcc.replace('V','')) >= vcc_min) and (int(MHz.replace('MHz','')) <= freq_max))
                                                    or ((float(vcc.replace('V','')) >= vcc_min2) and (int(MHz.replace('MHz','')) <= freq_max2))) and (result=='PASS'):
                Marginlist_tmp[PRECHG][EQLT][iref][dut] += 1
                if Marginlist_tmp[PRECHG][EQLT][iref][dut] == cmp_cnt:
                    Marginlist[PRECHG][EQLT][dut].append(float(Iref))
            #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return DATAlist,rows,Ireflist,Marginlist

def combine_DATAlist(DATAlist1,DATAlist2,testname2):
    DATAlist_tmp = {}
    try:
        DATAlist_tmp[testname2] = DATAlist2
        DATAlist2 = copy.deepcopy(DATAlist_tmp)
    finally:
        DATAlist_tmp = {}
    for testname in DATAlist2: 
        if testname in DATAlist1:
            for PRECHG in DATAlist2[testname]:  
                if PRECHG in DATAlist1[testname]:
                    for EQLT in DATAlist2[testname][PRECHG]:
                        if EQLT in DATAlist1[testname][PRECHG]:    
                            for iref in DATAlist2[testname][PRECHG][EQLT]:
                                if iref in DATAlist1[testname][PRECHG][EQLT]:
                                    for dut in DATAlist2[testname][PRECHG][EQLT][iref]:
                                        if dut in DATAlist1[testname][PRECHG][EQLT][iref]: 
                                            new_dut = str(int(list(DATAlist1[testname][PRECHG][EQLT][iref].keys())[-1]) + 1)
                                        else:
                                            new_dut = dut
                                        DATAlist1[testname][PRECHG][EQLT][iref].update(
                                            {new_dut:DATAlist2[testname][PRECHG][EQLT][iref][dut]})
                                else:
                                    DATAlist1[testname][PRECHG][EQLT].update({iref:DATAlist2[testname][PRECHG][EQLT][iref]})
                        else:
                            DATAlist1[testname][PRECHG].update({EQLT:DATAlist2[testname][PRECHG][EQLT]})
                else:
                    DATAlist1[testname].update({PRECHG:DATAlist2[testname][PRECHG]})
        else:
            DATAlist1.update({testname:DATAlist2[testname]})
    return DATAlist1

def combine_Marginlist(DATAlist1,DATAlist2,testname2):
    DATAlist_tmp = {}
    try:
        DATAlist_tmp[testname2] = DATAlist2
        DATAlist2 = copy.deepcopy(DATAlist_tmp)
    finally:
        DATAlist_tmp = {}
    for testname in DATAlist2: 
        if testname in DATAlist1:
            for PRECHG in DATAlist2[testname]:  
                if PRECHG in DATAlist1[testname]:
                    for EQLT in DATAlist2[testname][PRECHG]:
                        if EQLT in DATAlist1[testname][PRECHG]:    
                            for dut in DATAlist2[testname][PRECHG][EQLT]:
                                if dut in DATAlist1[testname][PRECHG][EQLT]: 
                                    new_dut = str(int(list(DATAlist1[testname][PRECHG][EQLT].keys())[-1]) + 1)
                                else:
                                    new_dut = dut
                                DATAlist1[testname][PRECHG][EQLT].update({new_dut:DATAlist2[testname][PRECHG][EQLT][dut]})
                        else:
                            DATAlist1[testname][PRECHG].update({EQLT:DATAlist2[testname][PRECHG][EQLT]})
                else:
                    DATAlist1[testname].update({PRECHG:DATAlist2[testname][PRECHG]})
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
    format1 = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','font_size': 36,'text_wrap':1})
    red_format = workbook.add_format({'bg_color':'FFC7CE','align': 'center','valign': 'vcenter'})
    green_format = workbook.add_format({'bg_color':'C6EFCE','align': 'center','valign': 'vcenter'})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+6)+':'+convert_to_string(endcol)+str(endrow), 
                                 {'type': 'text','criteria': 'containing','value': 'PASS','format': green_format})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+6)+':'+convert_to_string(endcol)+str(endrow),
                                 {'type': 'text','criteria': 'containing','value': 'FAIL','format': red_format})
    worksheet.merge_range(startrow + 0, startcol, startrow + 0, endcol - 2, printlist[0], format1)
    worksheet.merge_range(startrow + 1, startcol, startrow + 1, endcol - 2, 'PRECHG=' + printlist[1], format1)
    worksheet.merge_range(startrow + 2, startcol, startrow + 2, endcol - 2, 'EQLT=' + printlist[2], format1)
    worksheet.merge_range(startrow + 3, startcol, startrow + 3, endcol - 2, 'Iref=' + printlist[3] + '(%suA)'%printlist[4], format1)
    # worksheet.write(startrow + 0, startcol, printlist[0])
    # worksheet.write(startrow + 1, startcol, 'PRECHG=' + printlist[1])
    # worksheet.write(startrow + 2, startcol, 'EQLT=' + printlist[2])
    # worksheet.write(startrow + 3, startcol, 'Iref=' + printlist[3] + '(%suA)'%printlist[4])

def PrintMargin(ExcelWrite,Marginlist,i):
    row = 0
    col = 0
    flag = 0
    workbook = ExcelWrite.book
    format1 = workbook.add_format({'bold': True,'valign': 'vcenter','font_size': 14,'text_wrap':0})
    df = pd.DataFrame()
    df.to_excel(ExcelWrite, sheet_name = 'Margin_list')
    worksheets = ExcelWrite.sheets
    worksheet = worksheets['Margin_list']
    worksheet.write(row, col, 'VCC=(1.6~3.7)V', format1)
    worksheet.write(row + 1, col, 'Normal Freq=(10~56)MHz;Dual Freq=(10~108)MHz;Quad Freq=(10~80)MHz', format1)
    row += 3
    MAX_col = max({len(Marginlist[testname][PRECHG][EQLT][dut]) for testname in Marginlist       \
                    for PRECHG in Marginlist[testname] for EQLT in Marginlist[testname][PRECHG]  \
                    for dut in Marginlist[testname][PRECHG][EQLT]})
    for testname in Marginlist:
        for PRECHG in Marginlist[testname]:
            for EQLT in Marginlist[testname][PRECHG]:
                for dut in Marginlist[testname][PRECHG][EQLT]:
                    #if flag < 8:
                        #worksheet.write(row + (i + 2) * int(dut) - 1, col, 'Dut '+dut)
                        #flag += 1
                    worksheet.write(row + (i + 2) * int(dut), col + 0, testname)
                    worksheet.write(row + (i + 2) * int(dut), col + 1, 'Dut ' + dut)
                    worksheet.write(row + (i + 2) * int(dut), col + 2, 'PRECHG=' + PRECHG)
                    worksheet.write(row + (i + 2) * int(dut), col + 3, 'EQLT=' + EQLT)
                    for j,Iref in enumerate(sorted(Marginlist[testname][PRECHG][EQLT][dut],key = float)):
                        worksheet.write(row + (i + 2) * int(dut), col + 4 + j, '%suA'%Iref)
                    if Marginlist[testname][PRECHG][EQLT][dut] != []:
                        margin = '%.3fuA'%(float(max(Marginlist[testname][PRECHG][EQLT][dut])) - float(min(Marginlist[testname][PRECHG][EQLT][dut])))
                    else:
                        margin = 'NO_MARGIN'
                    worksheet.write(row + (i + 2) * int(dut), col + MAX_col + 6, margin)
                row += 1
    worksheet.set_column('A:B',12)

def data_to_excel(ExcelWrite,DATAlist,rows,Ireflist,Marginlist):
    i = 0
    printlist = [0 for i in range(5)]
    for testname in DATAlist:
        printlist[0] = testname
        for PRECHG in DATAlist[testname]:
            printlist[1] = PRECHG
            for EQLT in DATAlist[testname][PRECHG]:
                printlist[2] = EQLT
                Ireflist_tmp = copy.deepcopy(Ireflist[testname][PRECHG][EQLT])
                Ireflist_tmp = dict(sorted(Ireflist_tmp.items(), key=lambda x: float(x[1]['0'])))
                for j,iref in enumerate(Ireflist_tmp):
                    printlist[3] = iref
                #for j,iref in enumerate(DATAlist[testname][PRECHG][EQLT]):
                    #printlist[3] = iref
                    for dut in DATAlist[testname][PRECHG][EQLT][iref]:
                        printlist[4] = Ireflist[testname][PRECHG][EQLT][iref][dut]
                        df = pd.DataFrame(DATAlist[testname][PRECHG][EQLT][iref][dut])
                        df.index = rows
                        #df.to_excel(ExcelWrite, sheet_name = 'Dut' + dut, startrow = i * (df.shape[0] + 6) + 5, 
                        #            startcol= j * (df.shape[1] + 2) + 1, index = True, header = True)
                        
                        if not j:
                            df.to_excel(ExcelWrite, sheet_name = 'Dut' + dut, startrow=i * (df.shape[0] + 6) + 5,
                                        startcol=j * (df.shape[1]) + 1, index=True, header=True)
                        else:
                            df.to_excel(ExcelWrite, sheet_name = 'Dut' + dut, startrow=i * (df.shape[0] + 6) + 5,
                                        startcol=j * (df.shape[1]) + 2, index=False, header=True)
                    
                        start_row = i * (df.shape[0] + 6) + 1
                        #start_col = j * (df.shape[1] + 2) + 1
                        start_col = j * (df.shape[1]) + 2
                        end_row = start_row + df.shape[0] + 1 + 4
                        end_col = start_col + df.shape[1] + 1
                        set_excel_style(ExcelWrite, 'Dut' + dut, start_row, start_col, end_row, end_col, dut, printlist)
                i += 1
    PrintMargin(ExcelWrite,Marginlist,i)
    ExcelWrite.save()
    ExcelWrite.close()

if __name__ == '__main__':
    DATAlist_tmp = {}
    Ireflist_tmp = {}
    Marginlist_tmp = {}
    FAILflie_list = []
    root = tk.Tk()
    root.withdraw()
    #file_path = filedialog.askopenfilename()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    #file_list.sort(key= lambda x:int(re.findall(r"_j=([\d]{1,})_s[\d]{1,}\.txt", x)[0]))
    flielist_cmp = copy.deepcopy(file_list)
    for file in file_list:
        #try:
            print(file)
            raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file)
            testname = shotname.replace(re.findall(r"(_s[\d]{1,})", file)[0],'')
            DATAlist,rows,Ireflist,Marginlist = get_file_data(file,testname)
            DATAlist_tmp = combine_DATAlist(DATAlist_tmp,DATAlist,testname)
            Ireflist_tmp = combine_DATAlist(Ireflist_tmp,Ireflist,testname)
            Marginlist_tmp = combine_Marginlist(Marginlist_tmp,Marginlist,testname)
            del flielist_cmp[0]
            if all(raw_filepath not in file_cmp for file_cmp in flielist_cmp):
                pandas.io.formats.excel.header_style = None
                try:
                    #shotname = shotname.replace(re.findall(r"(_j=[\d]{1,}_s[\d]{1,})\.txt", file)[0],'')
                    shotname = shotname.replace(re.findall(r"(_s[\d]{1,})", file)[0],'')
                    #shotname = shotname.replace(re.findall(r"(_PRECHG=[\d]{1,}_s[\d]{1,})\.txt", file)[0],'')
                finally:
                    dest_filename = raw_filepath + r'/' + shotname + r'.xlsx'
                ExcelWrite = pd.ExcelWriter(dest_filename)
                data_to_excel(ExcelWrite,DATAlist_tmp,rows,Ireflist_tmp,Marginlist_tmp)
                #DATAlist_tmp = {}
        #except:
            #FAILflie_list.append(file)
            #ExcelWrite.save()
            #ExcelWrite.close()
    print('FAIL_list=' + str(FAILflie_list))

