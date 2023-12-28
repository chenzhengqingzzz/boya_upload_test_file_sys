# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 15:20:54 2023

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
        elif path.endswith('.asc'):
            file_list.append(path)
    return file_list

def get_file_data(file_path):
    start_flag = 0
    DATAlist = {}
    DATAlist.update({('DIEX','DIEY','ADDR'):['DIEX','DIEY','DUT','ADDR','BYTE'] + ['BIT%d'%(7-i) for i in range(8)]})
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if 'RD_PAGE0_LOG_AFM' in line:
            start_flag = 1
        elif 'TEST TIME' in line:
            start_flag = 0
        # DUT   258   DIEX   363   DIEY   255    ADDR=       0 BYTE=    0080
        searchObj = re.match(r"DUT[\s]{1,}([\d]{1,})[\s]{1,}DIEX[\s]{1,}([\d]{1,})[\s]{1,}DIEY[\s]{1,}([\d]{1,})[\s]{1,}ADDR=[\s]{1,}([0-9a-fA-F]{1,})[\s]{1,}BYTE=[\s]{1,}([0-9a-fA-F]{1,})", line)
        if searchObj and start_flag:
            DUT  = int(searchObj.group(1))
            DIEX = int(searchObj.group(2))
            DIEY = int(searchObj.group(3))
            ADDR = '0x%02x'%int(searchObj.group(4),16)
            BYTE = '0x%02x'%int(searchObj.group(5),16)
            if (DIEX,DIEY,ADDR) not in DATAlist:
                DATAlist.update({(DIEX,DIEY,ADDR):[DIEX,DIEY,DUT,ADDR,BYTE] + ['-' for i in range(8)]})
        # DUT   261   DIEX   243   DIEY   304    ADDR_Y=00000000000000000000000011110000 REFNO=     1    CUR_IREF= 20.00NA 
        searchObj = re.match(r"DUT[\s]{1,}([\d]{1,})[\s]{1,}DIEX[\s]{1,}([\d]{1,})[\s]{1,}DIEY[\s]{1,}([\d]{1,})[\s]{1,}ADDR_Y=([0-1]{1,})[\s]{1,}REFNO=[\s]{1,}([\d]{1,})[\s]{1,}CUR_IREF= (.*A)", line)
        if searchObj:
            DUT  = int(searchObj.group(1))
            DIEX = int(searchObj.group(2))
            DIEY = int(searchObj.group(3))
            # ADDR = '0x%02x'%int(searchObj.group(4),2)
            REFNO = int(searchObj.group(5))
            if REFNO<=8:
                ADDR = '0x%02x'%int(searchObj.group(4),2)
            else:
                REFNO -= 8
                ADDR = '0x%02x'%(int(searchObj.group(4),2)+1)
            CUR_IREF = searchObj.group(6)
            if 'NA' in CUR_IREF:
                CUR_IREF = '%.2fUA'%(float(CUR_IREF[:-2])*0.001)
            elif 'MA' in CUR_IREF:
                CUR_IREF = '%.2fUA'%(float(CUR_IREF[:-2])*1000)
            elif 'UA' not in CUR_IREF:
                CUR_IREF = '%.2fUA'%(float(CUR_IREF[:-2])*1000000)
            if (DIEX,DIEY,ADDR) in DATAlist and int(DATAlist[(DIEX,DIEY,ADDR)][4],16)&(1<<(REFNO-1)):
                DATAlist[(DIEX,DIEY,ADDR)][0-REFNO] = CUR_IREF
    return DATAlist

def data_to_excel(filepath,dest_filename,DATAlist):
    ExcelWrite = pd.ExcelWriter(dest_filename)
    for wafer in DATAlist:
        df = pd.DataFrame(DATAlist[wafer])
        df.T.to_excel(ExcelWrite,sheet_name = wafer,index=False,header=False,startrow=0,startcol=0)
    ExcelWrite.close()
    
if __name__ == '__main__':
    DATAlist = {}
    process_list = []
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    flielist_cmp = copy.deepcopy(file_list)
    for file in file_list:
        print(file)
        filepath, filepath1, filepath2, filename = get_file_info(file)
        raw_filepath, shotname, extension = get_filePath_fileName_fileExt(file)
        wafer = re.match(r".*log(.*)_tmp.*\.asc", file).group(1)[-2:]
        DATAlist.update({wafer:get_file_data(file)})
        flielist_cmp.remove(file)
        if all(raw_filepath not in file_cmp for file_cmp in flielist_cmp):
            dest_filename = raw_filepath + r'/' + shotname + r'.xlsx'
            process = Process(target = data_to_excel,args=(filepath2,dest_filename,DATAlist,))
            process_list.append(process)
            process.start()
            # DATAlist = {}
    for process in process_list:
        process.join()