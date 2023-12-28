# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 11:20:46 2023

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
    DATAlist = {}
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    logid = re.match(r".*log(.*)_by.*\.asc", file_path).group(1)[-2:]
    #DUT   257   DIEX   200   DIEY    17    SBIN=     1    VREF_BF_TRIM= 622.0MV  VREF= 610.0MV  IREF=-3.536UA  STANDBY= 10.70UA  DPD= 678.0NA  VPP= 1.892V   VREF_NEGP= 0.000V   NEGP=-3.192V   VPP25= 1.126V
    for line in lines:
        searchObj = re.match(r"DUT.*DIEX[\s]{1,}([\d]{1,})[\s]{1,}DIEY[\s]{1,}([\d]{1,})[\s]{1,}SBIN=[\s]{1,}1[\s]{1,}VREF_BF_TRIM= (.*)MV  VREF.*IREF.*STANDBY.*", line)
        if searchObj:
            DIEX = int(searchObj.group(1))
            DIEY = int(searchObj.group(2))
            VREF_BF_TRIM = float(searchObj.group(3))
            if logid not in DATAlist:
                DATAlist.update({logid+'_DIEX':[]})
                DATAlist.update({logid+'_DIEY':[]})
                DATAlist.update({logid:[]})
            DATAlist[logid+'_DIEX'].append(DIEX)
            DATAlist[logid+'_DIEY'].append(DIEY)
            DATAlist[logid].append(VREF_BF_TRIM)
    DATAlist[logid+'_DIEX'].insert(0,'DIEX')
    DATAlist[logid+'_DIEY'].insert(0,'DIEY')
    # DATAlist[logid].insert(0,'%d/%d'%(len(list(filter(lambda x: x<=540.0,DATAlist[logid]))),len(DATAlist[logid])))
    DATAlist[logid].insert(0,'%d/%d'%(len(list(filter(lambda x: x<=540.0,DATAlist[logid]))),33424))#40GW 82209, 80AW 51928, 16AW 33424
    return DATAlist

def data_to_excel(filepath,dest_filename,DATAlist):
    ExcelWrite = pd.ExcelWriter(dest_filename)
    df = pd.DataFrame.from_dict(DATAlist,orient='index')
    df.T.to_excel(ExcelWrite,sheet_name = filepath,startrow=0,startcol=0)
    # df.T.to_csv(dest_filename,index=False)
    ExcelWrite.save()
    
    
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
        DATAlist.update(get_file_data(file))
        flielist_cmp.remove(file)
        if all(raw_filepath not in file_cmp for file_cmp in flielist_cmp):
            dest_filename = raw_filepath + r'/' + shotname + r'.xlsx'
            # dest_filename = raw_filepath + r'/' + shotname + r'.csv'
            process = Process(target = data_to_excel,args=(filepath2,dest_filename,DATAlist,))
            process_list.append(process)
            process.start()
            DATAlist = {}
    for process in process_list:
        process.join()