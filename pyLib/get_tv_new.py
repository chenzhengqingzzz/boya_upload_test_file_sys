# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 19:36:20 2021

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
        if "bak(DC)" in lists:
            continue
        path = os.path.join(raw_path, lists) 
        if os.path.isdir(path): 
            get_filePath_list(path,file_list)
        elif path.endswith('.txt'):
            file_list.append(path)
    return file_list

def get_file_data(file_path):
    global bestflag
    rename_flag = 0
    rename = ['FIB2#Dut0','FIB2#Dut1','noFIB#Dut2','noFIB#Dut3','noFIB#Dut4','noFIB#Dut5','noFIB#Dut6','noFIB#Dut7']
    DATAlist = {}
    DATAlist_tv = {}
    bestlist_tv = {}
    freqlist_tv = {}
    rows = []
    f = open(file_path, 'r', encoding='UTF-8-sig')
    lines = f.readlines()
    f.close()
    for line in lines:
       # 40.0MHz QuadIO read 0F, VCC 1.6 V, VIH 1.0, VIL 0.0, tCLQV 8.1 ns, FAIL!!
       # Failing DUTs 0xf, Dut 0 40.0MHz compare_jedec_id_test, VCC 1.6 V, VIH 1.0, VIL 0.0, tCLQV 5.0 ns, FAIL!!
       # Failing DUTs 0xf, Dut 0 40.0MHz QuadIO read 0F, VCC 1.60 V, VIH 1.00, VIL 0.00, tCLQV 1.0 ns, FAIL!!
       searchObj = re.match(r'.*Failing.*, Dut (.*) .*MHz (.*), VCC (.*) V, VIH .*, VIL .*, tCLQ. (.*) ns, (.*)!!',line)
       # Failing DUTs 0xf, Dut 0 50MHz, eng_sec_erase_rd_ff, VCC 1.60 V, tCSH 0 ns, FAIL!!
       #searchObj = re.match(r'.*Failing.*, Dut (.*) *50MHz, (.*), VCC (.*) V, tCSH (.*) ns, (.*)!!',line)
       if searchObj:
           dut = int(searchObj.group(1)) + 4 * int(re.findall(r"_s(\d)\.txt", file)[-1])
           # if dut < 1 or dut > 3:
           #     continue
           if rename_flag:
               dut = '%s'%(rename[dut])
           else:
               dut = 'Dut%d'%dut
           testname = searchObj[2]
           vcc = searchObj[3]+'V'
           tCLQV = float(searchObj[4])
           result = searchObj[5]
           # if int(dut) > 1:
           #     continue
           if testname not in DATAlist:
               DATAlist.update({testname:{}})
               DATAlist_tv.update({testname:{}})
               bestlist_tv.update({testname:{}})
               freqlist_tv.update({testname:{}})
           if dut not in DATAlist[testname]:
               DATAlist[testname].update({dut:{}})
               DATAlist_tv[testname].update({dut:{}})
               bestlist_tv[testname].update({dut:{}})
               freqlist_tv[testname].update({dut:{}})
           if vcc not in DATAlist[testname][dut]:
               DATAlist[testname][dut].update({vcc:[]})
               DATAlist_tv[testname][dut].update({vcc:"NO_PASS"})
               bestlist_tv[testname][dut].update({vcc:"NO_PASS"})
               freqlist_tv[testname][dut].update({vcc:"NO_PASS"})
           if '%.1fns'%tCLQV not in rows:
               rows.append('%.1fns'%tCLQV)
           DATAlist[testname][dut][vcc].append(result)
           if ('PASS' in result) and (len(DATAlist[testname][dut][vcc])<2 or ('FAIL' in DATAlist[testname][dut][vcc][-2])):
               DATAlist_tv[testname][dut][vcc] = tCLQV
               #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
       # VCC:2.60V; best_tv DUT0 7.0ns 132.0MHz, DUT1 7.4ns 130.0MHz, DUT2 7.4ns 130.0MHz, DUT3 7.4ns 132.0MHz
       if 'best_tv' in line:
           bestflag = 1
           searchObj = re.match(r'.*VCC:(.*)V; best_tv DUT0 (.*)ns (.*)MHz, DUT1 (.*)ns (.*)MHz, DUT2 (.*)ns (.*)MHz, DUT3 (.*)ns (.*)MHz',line)
           if not searchObj:
               continue
           vcc = '%.1fV'%float(searchObj[1])
           if '0' in bestlist_tv[testname]:
               bestlist_tv[testname]['0'][vcc] = float(searchObj[2])
               freqlist_tv[testname]['0'][vcc] = float(searchObj[3])
           if '1' in bestlist_tv[testname]:
               bestlist_tv[testname]['1'][vcc] = float(searchObj[4])
               freqlist_tv[testname]['1'][vcc] = float(searchObj[5])
           if '2' in bestlist_tv[testname]:
               bestlist_tv[testname]['2'][vcc] = float(searchObj[6])
               freqlist_tv[testname]['2'][vcc] = float(searchObj[7])
           if '3' in bestlist_tv[testname]:
               bestlist_tv[testname]['3'][vcc] = float(searchObj[8])
               freqlist_tv[testname]['3'][vcc] = float(searchObj[9])
    return DATAlist_tv,DATAlist,rows,bestlist_tv,freqlist_tv

def PrinttCLQV(ExcelWrite,DATAlist_tv,bestlist_tv,freqlist_tv):
    global bestflag
    row = 1
    col = 1
    flag = 1
    workbook = ExcelWrite.book
    format1 = workbook.add_format({'bold': True,'valign': 'vcenter','font_size': 14,'text_wrap':0})
    format2 = workbook.add_format({'bold': True,'valign': 'vcenter','text_wrap':0})
    format3 = workbook.add_format({'bold': 0, 'valign': 'vcenter', 'font_size': 11, 'text_wrap': 0, 'num_format': '0.0'})
    df = pd.DataFrame()
    df.to_excel(ExcelWrite, sheet_name = 'DATAlist_tv')
    worksheets = ExcelWrite.sheets
    worksheet = worksheets['DATAlist_tv']
    for testname in DATAlist_tv:
        worksheet.write(row, col, testname, format1)
        flag = 1
        row += 1
        chart_col = workbook.add_chart({'type': 'line'})
        for i,dut in enumerate(DATAlist_tv[testname]):
            if type(dut) == str:
                worksheet.write(row + i + 1, col + 0, dut)
            else:
                worksheet.write(row + i + 1, col + 0, 'Dut%d'%int(dut))
            if bestflag:
                if i==0:
                    worksheet.write(row-1, col + len(DATAlist_tv[testname][dut]) + 13, 'MaxFreqTv_'+testname, format1)
                    worksheet.write(row-1, col + 2*len(DATAlist_tv[testname][dut]) + 16, 'MaxFreq_'+testname, format1)
                if type(dut) == str:
                    worksheet.write(row + i + 1, col + 0 + len(DATAlist_tv[testname][dut]) + 13, '%s'%(dut))
                    worksheet.write(row + i + 1, col + 0 + 2*len(DATAlist_tv[testname][dut]) + 16, '%s'%(dut))
                else:
                    worksheet.write(row + i + 1, col + 0 + len(DATAlist_tv[testname][dut]) + 13, 'Dut%d'%(dut))
                    worksheet.write(row + i + 1, col + 0 + 2*len(DATAlist_tv[testname][dut]) + 16, 'Dut%d'%(dut))
                    
            for j,vcc in enumerate(DATAlist_tv[testname][dut]):
                if flag:
                    worksheet.write(row, col + j + 1, vcc,format2)
                worksheet.write(row + i + 1, col + j + 1, DATAlist_tv[testname][dut][vcc],format3)
                if bestflag:
                    if flag:
                        worksheet.write(row, col + j + 1 + len(DATAlist_tv[testname][dut]) + 13, vcc,format2)
                        worksheet.write(row, col + j + 1 + 2*len(DATAlist_tv[testname][dut]) + 16, vcc,format2)
                    worksheet.write(row + i + 1, col + j + 1 + len(DATAlist_tv[testname][dut]) + 13, bestlist_tv[testname][dut][vcc],format3)
                    worksheet.write(row + i + 1, col + j + 1 + 2*len(DATAlist_tv[testname][dut]) + 16, freqlist_tv[testname][dut][vcc])
            # 配置第一个系列数据
            chart_col.add_series({
                'name':'=DATAlist_tv!'+convert_to_string(col)+str(row+i+2),
                'categories':'=DATAlist_tv!'+convert_to_string(col+1)+str(row+1)+':'+convert_to_string(col+len(DATAlist_tv[testname][dut]))+str(row+1),
                'values':'=DATAlist_tv!'+convert_to_string(col+1)+str(row+i+2)+':'+convert_to_string(col+len(DATAlist_tv[testname][dut]))+str(row+i+2),
            })
            flag = 0
        # 设置图表的title 和 x，y轴信息
        chart_col.set_title({'name':testname})
        chart_col.set_x_axis({'name':'VCC (V)'})
        chart_col.set_y_axis({'name':'tV (ns)'})
        chart_col.set_size({'height':12*18,'width':8*64})
        
        # 设置图表的风格
        chart_col.set_style(2)
        
        # 把图表插入到worksheet并设置偏移
        worksheet.insert_chart(convert_to_string(col+len(DATAlist_tv[testname][dut])+3)+str(row), chart_col, {'x_offset': 0, 'y_offset': 0})
        
        row += i + 3
    workbook.close()

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

def set_excel_style(writer,sheet_name,startrow,startcol,endrow,endcol,dut,testname):
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

def combine_DATAlist(DATAlist1,DATAlist2,testname2):
    DATAlist_tmp = {}
    try:
        for i,testname in enumerate(DATAlist2):
            DATAlist_tmp[testname2[i]] = DATAlist2[testname]
        DATAlist2 = copy.deepcopy(DATAlist_tmp)
    finally:
        DATAlist_tmp = {}
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

def data_to_excel(ExcelWrite,DATAlist,rows_list,DATAlist_tv_tmp,bestlist_tv,freqlist_tv):
    for j,testname in enumerate(DATAlist):
        k=0
        for i,dut in enumerate(DATAlist[testname]):
            #if i > 1:
                #continue
            #print(testname)
            df = pd.DataFrame(DATAlist[testname][dut])
            df.index = rows_list[testname]
            if 'down' in testname:
                k=1
                testname2 = testname.replace('_down','')
            elif 'up' in testname:
                testname2 = testname.replace('_up','')
            else:
                testname2 = testname
            df.to_excel(ExcelWrite, sheet_name = testname2, startrow = i * (df.shape[0] + 3) + 2, 
                            startcol= k * (df.shape[1] + 3) + 2, index = True, header = True)
            start_row = i * (df.shape[0] + 3) + 1
            start_col = k * (df.shape[1] + 3) + 1
            end_row = start_row + df.shape[0] + 1
            end_col = start_col + df.shape[1] + 1
            set_excel_style(ExcelWrite, testname2, start_row, start_col, end_row, end_col, 'Dut' + dut, testname)
    PrinttCLQV(ExcelWrite,DATAlist_tv_tmp,bestlist_tv,freqlist_tv)
    ExcelWrite.close()
    
def renamefilelist(filelist):
    newfilelist = []
    for file in filelist:
        filepath, filename = os.path.split(file)
        newfile = filename.replace('_test_','_')
        newfile = newfile.replace('_double_','_')
        newfile = newfile.replace('_compare_','_')
        newfile = newfile.replace('_chip_','_')
        if ('random' in file) or ('by32' in file):
            newfile = newfile.replace('_random_','_')
        if newfile != filename:
            newfile = os.path.join(filepath, newfile)
            os.rename(file, newfile)
        newfilelist.append(newfile)
    return newfilelist

def custom_sort_key(file_path):
    parts = re.split(r'(\d+)', os.path.basename(file_path))
    parts = [int(part) if part.isdigit() else part for part in parts]
    return parts

if __name__ == '__main__':
    bestflag = 0
    DATAlist_tmp = {}
    DATAlist_tv_tmp = {}
    bestlist_tv_tmp = {}
    freqlist_tv_tmp = {}
    rows_list = {}
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    file_list = renamefilelist(file_list)
    file_list = get_filePath_list(file_path,file_list = [])
    file_list.sort(key=custom_sort_key)
    flielist_cmp = copy.deepcopy(file_list)
    for file in file_list:
        print(file)
        filepath, shotname, extension = get_filePath_fileName_fileExt(file)
        shotname = shotname.replace(re.findall(r"(_s[\d]{1,})\.txt", file)[0],'')
        #shotname = shotname.replace(re.findall(r"\.txt", file)[0],'')
        testname = [shotname]
        DATAlist_tv,DATAlist,rows,bestlist_tv,freqlist_tv = get_file_data(file)
        if rows != []:
            rows_list.update({shotname:rows})
            DATAlist_tmp = combine_DATAlist(DATAlist_tmp,DATAlist,testname)
            DATAlist_tv_tmp = combine_DATAlist(DATAlist_tv_tmp,DATAlist_tv,testname)
            bestlist_tv_tmp = combine_DATAlist(bestlist_tv_tmp,bestlist_tv,testname)
            freqlist_tv_tmp = combine_DATAlist(freqlist_tv_tmp,freqlist_tv,testname)
        del flielist_cmp[0]
        if all(filepath not in file_cmp for file_cmp in flielist_cmp):
            pandas.io.formats.excel.header_style = None
            dest_filename = filepath + r'/' + shotname + r'.xlsx'
            ExcelWrite = pd.ExcelWriter(dest_filename)
            try:
                data_to_excel(ExcelWrite,DATAlist_tmp,rows_list,DATAlist_tv_tmp,bestlist_tv_tmp,freqlist_tv_tmp)
            finally:
                ExcelWrite.close()


    