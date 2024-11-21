# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 10:01:53 2021

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

def get_file_info(filepath):
    (filepath, filename) = os.path.split(filepath)
    (filepath, filepath2) = os.path.split(filepath)
    (filepath, filepath1) = os.path.split(filepath)
    return filepath, filepath1, filepath2, filename

def get_filePath_list(raw_path,file_list = []): 
    for lists in os.listdir(raw_path): 
        path = os.path.join(raw_path, lists) 
        if os.path.isdir(path): 
            get_filePath_list(path,file_list)
        elif path.endswith('.txt'):
            file_list.append(path)
    return file_list

def get_file_data(file_path):
    ATE = 'PK2'
    rename_flag = 1
    # rename = ['FIB7(DRV100%)','FIB7(DRV100%)','FIB15(DRV75%)','FIB15(DRV75%)','noFIB','noFIB','noFIB','noFIB']
    # rename = ['FIB27#10','FIB27#13','FIB28#6','FIB28#7','noChip','noChip','noChip','noChip']
    rename = ['fuseE0-2','fuseE0-2','fuseE0-2','fuseE0-2','fuseE4','fuseE4','fuseE4','fuseE4']
    # rename = ['noFIB','noFIB','noFIB','noFIB','FIB23#34','FIB23#35','FIB27#41','FIB27#47','PY128','noChip','noChip','noChip']
    DATAlist = {}
    FreqMAXList = {}
    rows_list = {}
    tv_list = {}
    searchObj2 = 0
    searchObj3 = 0
    freqCmpLimit = 0
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    #raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file_path)
    #testname = str(shotname.replace(re.findall(r"(_s[\d]{1,})\.txt", file_path)[0],''))
    #if testname not in DATAlist:
        #DATAlist.update({testname:{}})
        #FreqMAXList.update({testname:{}})
    for line in lines:
        #*** Test name：um_random_pgm_dual_byte_to_page, Failing DUTs 0x0, Dut 0 11.00 ns, 1.60 V, 2.00 MHz, PASS!!***
        #Failing DUTs 0x0, Dut 0, 1.60 V, 10.00 MHz, 0x0000 PASS!!
        #searchObj = re.match(r".*Failing.*, Dut (.*) .* ns, (.*) V, (.*) MHz, (.*)!!", line)
        #searchObj = re.match(r".*Failing.*, Dut (.*), (.*) V, (.*) MHz, (.*)!!", line)
        searchObj = re.match(r".*Failing.*, Dut (\d+).*, (.*) V, (.*) MHz, (.*)!!", line)
        #searchObj = re.match(r".*Failing.*, Dut (.*), (.*) V, (.*) MHz (.*)!!", line)
        #Failing DUTs 0x0, Dut 0, VCC_brownout 0.0 V, delay_time 150.00 ms, PASS!!
        #searchObj = re.match(r".*Failing.*, Dut ([\d+]).*, VCC_brownout (.*) V, delay_time (.*) ms, (.*)!!", line)
        if 'Test name' in line:
            searchObj1 = re.match(r".*Test name.(.*), Failing", line)
        elif 'test name' in line:
            #searchObj1 = re.match(r".*test name. (.*) start", line)
            searchObj1 = re.match(r".*test name. (.*)\s..*", line)
        elif 'dummy_cnt' in line:
            searchObj2 = re.match(r".*dummy_cnt = (\d) .*", line)
        elif 'strobe:' in line:
            searchObj3 = re.match(r".*strobe: (.*)\s..*", line)
        else:
            searchObj1 = 0
            # raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file_path)
            # testname = str(shotname.replace(re.findall(r"(_s[\d]{1,})\.txt", file)[0],''))
            # if testname not in DATAlist:
            #     DATAlist.update({testname:{}})
        if searchObj1:
            testname = str(searchObj1.group(1))
            if testname not in DATAlist:
                DATAlist.update({testname:{}})
                FreqMAXList.update({testname:{}})
                rows_list.update({testname:[]})
            # if searchObj2:
            #     testname = testname+'_dummy'+str(searchObj2.group(1))
            #     if testname not in DATAlist:
            #         DATAlist.update({testname:{}})
            #         FreqMAXList.update({testname:{}})
            #         rows_list.update({testname:[]})
        if searchObj:
            if ATE == 'M2':
                dut = int(searchObj.group(1)) + 16 * int(re.findall(r"_s(\d)\.txt", file)[-1])   #M2
            else:
                dut = int(searchObj.group(1)) + 4 * int(re.findall(r"_s(\d)\.txt", file)[-1])
            # if dut < 1 or dut > 3:
            #     continue
            if rename_flag:
                dut = '%s#Dut%d'%(rename[dut],dut)
            else:
                dut = 'Dut%d'%dut
           # tv = searchObj.group(2) + 'ns'
            vcc = searchObj.group(2) + 'V'
            #MHz = str(int(float(searchObj.group(3)))) + 'MHz'
            MHz = str(float(searchObj.group(3))) + 'MHz'
            result = searchObj.group(4)
            # if int(searchObj.group(1)) > 1:
            #     continue
            if dut not in DATAlist[testname]:
                DATAlist[testname].update({dut:{}})
                FreqMAXList[testname].update({dut:{}})
            if vcc not in DATAlist[testname][dut]:
                DATAlist[testname][dut].update({vcc:[]})
                FreqMAXList[testname][dut].update({vcc:'MAX'})
            if MHz not in rows_list[testname]:
                rows_list[testname].append(MHz)
            if searchObj3:
                tv = searchObj3.group(1)
                if testname not in tv_list:
                    tv_list.update({testname:{}})
                if vcc not in tv_list[testname]:
                    tv_list[testname].update({vcc:tv})
                else:
                    tv_list[testname][vcc] = tv
                searchObj3 = 0
            if len(DATAlist[testname][dut][vcc]) - rows_list[testname].index(MHz):
                DATAlist[testname][dut][vcc][rows_list[testname].index(MHz)] = result
            else:
                DATAlist[testname][dut][vcc].append(result)
            if FreqMAXList[testname][dut][vcc] != 'MAX' and rows_list[testname].index(MHz) == 0:
                FreqMAXList[testname][dut][vcc] = 'MAX'
            if result == 'FAIL':
                limitL = next((i for i, freq in enumerate(rows_list[testname]) if float(freq.replace('MHz','')) >= freqCmpLimit), 0)
                if 'FAIL' in DATAlist[testname][dut][vcc][limitL:]:
                    if DATAlist[testname][dut][vcc][limitL:].index('FAIL'):
                        MAXFreq = float(rows_list[testname][DATAlist[testname][dut][vcc][limitL:].index('FAIL')-1+limitL].replace('MHz',''))
                    elif DATAlist[testname][dut][vcc].index('FAIL'):
                        MAXFreq = float(rows_list[testname][DATAlist[testname][dut][vcc].index('FAIL')-1].replace('MHz',''))
                    else:
                        MAXFreq = 0
                    FreqMAXList[testname][dut][vcc] = MAXFreq
                        
                # if DATAlist[testname][dut][vcc].index('FAIL'):
                #     MAXFreq = float(rows_list[testname][DATAlist[testname][dut][vcc].index('FAIL')-1].replace('MHz',''))
                # else:
                #     MAXFreq = 0
                # FreqMAXList[testname][dut][vcc] = MAXFreq
            # if result == 'FAIL' and rows_list[testname].index(MHz):
            #     MAXFreq = float(rows_list[testname][rows_list[testname].index(MHz) - 1].replace('MHz',''))
            # else:
            #     MAXFreq = 0
            # if result == 'FAIL' and ((FreqMAXList[testname][dut][vcc] == 'MAX') or (FreqMAXList[testname][dut][vcc] > MAXFreq)) \
            #                     and (len(DATAlist[testname][dut][vcc])<2 or DATAlist[testname][dut][vcc][rows_list[testname].index(MHz)-1] == 'PASS'):
            #     FreqMAXList[testname][dut][vcc] = MAXFreq
                #if rows_list[testname].index(MHz):
                   #FreqMAXList[testname][dut][vcc] = int(rows_list[testname][rows_list[testname].index(MHz) - 1].replace('MHz',''))
                   #FreqMAXList[testname][dut][vcc] = MAXFreq
                #else:
                   #FreqMAXList[testname][dut][vcc] = 0
            #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return FreqMAXList,DATAlist,rows_list,tv_list

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

def PrinttFreqMAX(ExcelWrite,row_list,FreqMAXList):
    row = 1
    col = 1
    flag = 1
    workbook = ExcelWrite.book
    format1 = workbook.add_format({'bold': True,'valign': 'vcenter','font_size': 14,'text_wrap':0})
    format2 = workbook.add_format({'bold': True,'valign': 'vcenter','text_wrap':0})
    format3 = workbook.add_format({'bold': True,'valign': 'vcenter','text_wrap':0,'font_color':'FF0000'})
    df = pd.DataFrame()
    df.to_excel(ExcelWrite, sheet_name = 'FreqMAXList')
    worksheets = ExcelWrite.sheets
    worksheet = worksheets['FreqMAXList']
    for mode in FreqMAXList:
        for testname in FreqMAXList[mode]:
            # worksheet.write(row, col, mode +'-'+ testname, format1)
            worksheet.write(row, col, fixDummy(testname), format1)
            flag = 1
            row += 1
            chart_col = workbook.add_chart({'type': 'line'})
            # del FreqMAXList[mode][testname]['Dut3']
            # del FreqMAXList[mode][testname]['Dut4']
            # del FreqMAXList[mode][testname]['Dut5']
            for k,dut in enumerate(FreqMAXList[mode][testname]):
                if len(FreqMAXList[mode][testname])>8:
                    i = k
                else:
                    i = int(re.search(r'(Dut|DUT|dut)(\d+)', dut)[2])
                # if i>1:
                #     continue
                worksheet.write(row + i + 1, col + 0, dut)
                # if not i:
                #     MAX_col = len(FreqMAXList[mode][testname][dut])
                if not k:
                    MAX_col = len(FreqMAXList[mode][testname][dut])
                for j,vcc in enumerate(FreqMAXList[mode][testname][dut]):
                    if flag:
                        worksheet.write(row, col + j + 1, vcc,format2)
                    if FreqMAXList[mode][testname][dut][vcc] == 'MAX':
                        FreqMAXList[mode][testname][dut][vcc] = float(row_list[testname][-1].replace('MHz',''))
                    worksheet.write(row + i + 1, col + j + 1, FreqMAXList[mode][testname][dut][vcc])
                    # if not (('HT' in testname and dut == 'Dut1') or ('LT' in testname and dut == 'Dut3') or ('RT' in testname and (dut == 'Dut3' or dut == 'Dut4'))):
                    #     worksheet.write(row + i + 1, col + j + 1, FreqMAXList[mode][testname][dut][vcc])
                    # if not (('RT' in testname and (dut == 'Dut2'))):
                    #     worksheet.write(row + i + 1, col + j + 1, FreqMAXList[mode][testname][dut][vcc])
                # 配置第一个系列数据
                chart_col.add_series({
                    'name':'=FreqMAXList!'+convert_to_string(col)+str(row+i+2),
                    'categories':'=FreqMAXList!'+convert_to_string(col+1)+str(row+1)+':'+convert_to_string(col+len(FreqMAXList[mode][testname][dut]))+str(row+1),
                    'values':'=FreqMAXList!'+convert_to_string(col+1)+str(row+i+2)+':'+convert_to_string(col+len(FreqMAXList[mode][testname][dut]))+str(row+i+2),
                })
                flag = 0
                
            # 设置图表的title 和 x，y轴信息
            # chart_col.set_title({'name':mode +'-'+ testname})
            chart_col.set_title({'name': fixDummy(testname)})
            chart_col.set_x_axis({'name':'VCC (V)'})
            # chart_col.set_x_axis({'name':'tV (V)'})
            chart_col.set_y_axis({'name':'Freq (MHz)'})
            chart_col.set_size({'height':(len(FreqMAXList[mode][testname])+4)*18,'width':8*64})
            
            # 设置图表的风格
            chart_col.set_style(2)
            
            # 把图表插入到worksheet并设置偏移
            worksheet.insert_chart(convert_to_string(col+len(FreqMAXList[mode][testname][dut])+3)+str(row), chart_col, {'x_offset': 0, 'y_offset': 0})
            worksheet.write(row - 1, col + MAX_col - 1, 'MAXFreq:', format3)
            worksheet.write(row - 1, col + MAX_col, '=MIN(%s:%s)'%(convert_to_string(col + 1)+str(row + 2),convert_to_string(col + MAX_col)+str(row + len(FreqMAXList[mode][testname]) + 1)), format3)
            row += i + 3
    workbook.close()

def combine_DATAlist1(DATAlist1,DATAlist2):
    for datatmp in DATAlist2:
        if datatmp in DATAlist1 and 'Dut' in datatmp and all(data in DATAlist1[datatmp] for data in list(DATAlist2[datatmp].keys())):
            if len(DATAlist1[datatmp]) == len(DATAlist2[datatmp]):
                datatmp2 = 'Dut' + str(int(re.match(r"Dut(.*)", list(DATAlist1.keys())[-1])[1]) + 1)
                DATAlist1.update({datatmp2:DATAlist2[datatmp]})
            else:
                dutLenList = [len(DATAlist1[temp]) for temp in DATAlist1]
                datatmp2 = 'Dut%d'%(dutLenList.index(min(dutLenList)))
                DATAlist1[datatmp2].update(DATAlist2[datatmp])
        elif datatmp in DATAlist1:
            if type(DATAlist1) == dict:
                DATAlist1[datatmp] = combine_DATAlist1(DATAlist1[datatmp],DATAlist2[datatmp])
        else:
            if type(DATAlist1) == dict:
                DATAlist1.update({datatmp:DATAlist2[datatmp]})
            elif type(DATAlist1) == list:
                DATAlist1.append(datatmp)
    return DATAlist1

def combine_DATAlist(DATAlist1,DATAlist2,testname2,mode):
    DATAlist_tmp = {}
    try:
        for i,testname in enumerate(DATAlist2):
            DATAlist_tmp[testname2[i]] = DATAlist2[testname]
        DATAlist2 = copy.deepcopy(DATAlist_tmp)
    finally:
        DATAlist_tmp = {}
    if mode not in DATAlist1:
        DATAlist1.update({mode:{}})
    DATAlist1[mode] = combine_DATAlist1(DATAlist1[mode],DATAlist2)
    return DATAlist1
    
def set_excel_style(writer,sheet_name,startrow,startcol,endrow,endcol,dut,testname,tvlist):
    worksheets = writer.sheets
    worksheet = worksheets[sheet_name]
    #worksheet.hide_gridlines(option=2)
    workbook = writer.book  
    format1 = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','font_size': 24,'text_wrap':1})
    red_format = workbook.add_format({'bg_color':'FFC7CE','align': 'center','valign': 'vcenter'})
    green_format = workbook.add_format({'bg_color':'C6EFCE','align': 'center','valign': 'vcenter'})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+3)+':'+convert_to_string(endcol)+str(endrow+1), 
                                 {'type': 'text','criteria': 'containing','value': 'PASS','format': green_format})
    worksheet.conditional_format(convert_to_string(startcol)+str(startrow+3)+':'+convert_to_string(endcol)+str(endrow+1),
                                 {'type': 'text','criteria': 'containing','value': 'FAIL','format': red_format})
    worksheet.merge_range(startrow + 1, startcol, endrow, startcol, dut, format1)
    worksheet.merge_range(startrow, startcol, startrow, endcol, testname, format1)
    worksheet.set_column('B:B',8)
    if testname in tvlist:
        for i,vcc in enumerate(tvlist[testname]):
            worksheet.write(startrow - 1, startcol + 2 + i, tvlist[testname][vcc])
    #worksheet.set_column('B:B',12,format1)

def fixDummy(testname):
    flag=0
    if not flag:
        return testname
    if 'volt_freq' in testname:
        return testname
    if 'SPI' in testname:
        if 'DTR' in testname:
            return re.sub(r"_dummy_(\d+)", lambda x: "_dummy_%d"%(int(x.group(1))+1), testname)
        if ('dualio' in testname or 'dio' in testname or 'quadio' in testname or 'qio' in testname)\
            and ('continue' in testname or 'ctn' in testname):
            return re.sub(r"_dummy_(\d+)", lambda x: "_dummy_%d"%(int(x.group(1))+2), testname)
    if 'QPI' in testname:
        return re.sub(r"reg_(.*)h_dummy_(\d+)", 
                       lambda x: "reg_%02xh_dummy_%d" % (int(x.group(1), 16), ((int(x.group(1), 16) & 0x70) >> 4) * 2 + 4), 
                       testname)
    return testname

def data_to_excel(ExcelWrite,DATAlist,row_list,row_list2,FreqMAXList,tvlist):
    for mode in DATAlist:
        start_col = 1
        for j,testname in enumerate(DATAlist[mode]):
            # del DATAlist[mode][testname]['Dut3']
            # del DATAlist[mode][testname]['Dut4']
            # del DATAlist[mode][testname]['Dut5']
            for i,dut in enumerate(DATAlist[mode][testname]):
                # if i>1:
                #     continue
                #print(testname,dut)
                df = pd.DataFrame(DATAlist[mode][testname][dut])
                df.index = row_list[testname]
                if len(mode) > 31:
                    sheetname = mode[-31:]
                else:
                    sheetname = mode
                # df.to_excel(ExcelWrite, sheet_name = sheetname, startrow = i * (df.shape[0] + 3) + 2, 
                #             startcol= j * (df.shape[1] + 3) + 2, index = True, header = True)
                df.to_excel(ExcelWrite, sheet_name = sheetname, startrow = i * (df.shape[0] + 3) + 2, 
                            startcol= start_col + 1, index = True, header = True)
                start_row = i * (df.shape[0] + 3) + 1
                # start_col = j * (df.shape[1] + 3) + 1
                end_row = start_row + df.shape[0] + 1
                end_col = start_col + df.shape[1] + 1
                # set_excel_style(ExcelWrite, sheetname, start_row, start_col, end_row, end_col, dut, testname, tvlist)
                set_excel_style(ExcelWrite, sheetname, start_row, start_col, end_row, end_col, dut, fixDummy(testname), tvlist)
            start_col += (df.shape[1] + 3)
    PrinttFreqMAX(ExcelWrite,row_list2,FreqMAXList)
    # ExcelWrite.save()
    ExcelWrite.close()

def custom_sort_key(file_path):
    parts = re.split(r'(\d+)', os.path.basename(file_path))
    parts = [int(part) if part.isdigit() else part for part in parts]
    return parts

if __name__ == '__main__':
    DATAlist_all = {}
    FreqMAXList_all = {}
    DATAlist_tmp = {}
    FreqMAXList_tmp = {}
    FAILflie_list = []
    tvlist_tmp = {}
    row_list = {}
    row_list2 = {}
    root = tk.Tk()
    root.withdraw()
    #file_path = filedialog.askopenfilename()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    file_list.sort(key=custom_sort_key)
    flielist_cmp = copy.deepcopy(file_list)
    for file in file_list:
        #try:
            print(file)
            filepath, filepath1, filepath2, filename = get_file_info(file)
            raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file)
            try:
                #filepath1 = filepath1.replace(re.findall(r"(\(.*\))", filepath1)[0],'')
                shotname = shotname.replace(re.findall(r"(_s[\d]{1,})\.txt", file)[0],'')
            finally:
                dest_filename = raw_filepath + r'/' + shotname + r'.xlsx'
            FreqMAXList,DATAlist,rows,tv_list = get_file_data(file)
            str1 = re.findall(r'([HLR]T\([\-0-9C]+\))',file) or re.findall(r'([HLR]T[\-0-9C]+)',file)
            if(str1==[]):
                str1 = re.findall(r'([HLR]T)',file)
            str2 = re.findall(r'([modeMODE]{4}\d)', file)
            if str1!=[] and str2!=[]:
                sheetname = '%s_%s'%(str1[-1],str2[-1])
            else:
                sheetname = shotname[-31:]
            #testname = list(map(lambda x: x , list(DATAlist.keys())))
            # testname = list(map(lambda x: filepath2 + '-' + x, list(DATAlist.keys())))
            # testname = list(map(lambda x: x + '-' + shotname, list(DATAlist.keys())))
            testname = list(map(lambda x: shotname + '-' + x, list(DATAlist.keys())))
            if str2 != []:
                testname2 = list(map(lambda x: shotname.replace('_%s'%str2[-1], '') + '-' + x, list(DATAlist.keys())))
            else:
                testname2 = testname
            # testname = list(map(lambda x: shotname[-8:] + '-' + x, list(DATAlist.keys())))
            rows = dict(zip(testname, rows.values()))
            rows2 = dict(zip(testname2, rows.values()))
            # row_list.update(rows)
            row_list = combine_DATAlist1(row_list,rows)
            row_list2 = combine_DATAlist1(row_list2,rows2)
            for testname_old in tv_list:
                testname_new = filepath2 + '-' + testname_old
                # testname_new = shotname[-8:] + '-' + testname_old
                if testname_new not in tvlist_tmp:
                    tvlist_tmp.update({testname_new:copy.deepcopy(tv_list[testname_old])})
                else:
                    tvlist_tmp[testname_new] = copy.deepcopy(tv_list[testname_old])
            if file_path in filepath:
                DATAlist_all = combine_DATAlist(DATAlist_all,DATAlist,testname,sheetname)
                if str2 != []:
                    FreqMAXList_all = combine_DATAlist(FreqMAXList_all,FreqMAXList,testname2,sheetname.replace('_%s'%str2[-1], ''))
                else:
                    FreqMAXList_all = combine_DATAlist(FreqMAXList_all,FreqMAXList,testname2,sheetname)
            DATAlist_tmp = combine_DATAlist(DATAlist_tmp,DATAlist,testname,sheetname)
            if str2 != []:
                FreqMAXList_tmp = combine_DATAlist(FreqMAXList_tmp,FreqMAXList,testname2,sheetname.replace('_%s'%str2[-1], ''))
            else:
                FreqMAXList_tmp = combine_DATAlist(FreqMAXList_tmp,FreqMAXList,testname2,sheetname)
            pandas.io.formats.excel.header_style = None
            del flielist_cmp[0]
            if all(raw_filepath not in file_cmp for file_cmp in flielist_cmp):
                ExcelWrite = pd.ExcelWriter(dest_filename)
                data_to_excel(ExcelWrite,DATAlist_tmp,row_list,row_list2,FreqMAXList_tmp,tvlist_tmp)
                DATAlist_tmp = {}
                FreqMAXList_tmp = {}
            if all(filepath not in file_cmp for file_cmp in flielist_cmp) and (file_path in filepath):
                ExcelWrite_all = pd.ExcelWriter(filepath + r'/' + shotname + r'_all.xlsx')
                data_to_excel(ExcelWrite_all,DATAlist_all,row_list,row_list2,FreqMAXList_all,tvlist_tmp)
                DATAlist_all = {}
                FreqMAXList_all = {}
        #except:
            #FAILflie_list.append(file)
            #ExcelWrite.save()
            #ExcelWrite.close()
    print(FAILflie_list)

    
    
