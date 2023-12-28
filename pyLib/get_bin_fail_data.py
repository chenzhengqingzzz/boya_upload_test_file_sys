# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 16:16:35 2023

@author: LZJ
"""

import os
from tkinter import filedialog
import tkinter as tk
from multiprocessing import Process
import openpyxl


def get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension

def get_filePath_list(raw_path,file_list = []):
    for lists in os.listdir(raw_path):
        path = os.path.join(raw_path, lists)
        if os.path.isdir(path):
            get_filePath_list(path,file_list)
        elif path.endswith('.bin'):
            file_list.append(path)
    return file_list

def get_fail_addr_data(file):
    print('%s start' % file)
    filepath, shotname, extension = get_filePath_fileName_fileExt(file)
    file_out = '%s/%s.txt' % (filepath, shotname)
    wb=openpyxl.Workbook()
    ws=wb.create_sheet(index=0,title='shotname')
    binfile = open(file, 'rb')
    filewrite = open(file_out, 'w+')
    size = os.path.getsize(file)
    if size > 0:
        filewrite.write('FAIL_ADDR, FAIL_DATA, FAIL_BIT')
        list1 = ['FAIL_ADDR', 'FAIL_DATA', 'FAIL_BIT']
        A = 24
        B = 3
        while A > 0:
            A -= 1
            filewrite.write(', A%d'%A)
            list1.append('A%d'%A)
        while B > 0:
            B -= 1
            filewrite.write(', B%d'%B)
            list1.append('B%d'%B)
        filewrite.write('\n')
        ws.append(list1)
    for i in range(size):
        data = int.from_bytes(binfile.read(1), byteorder='big', signed=False)
        BIT = 8
        while BIT > 0:
            BIT -= 1
            if (i%128) < 16 and (data>>BIT&0x1) != 1:
                filewrite.write('0x%06X, %02Xh, BIT%d'%(i,data,BIT))
                list2 = ['0x%06X'%i, '%02Xh'%data, 'BIT%d'%BIT]
                A = 24
                B = 3
                while A > 0:
                    A -= 1
                    filewrite.write(', %d'%(i>>A&0x1))
                    list2.append('%d'%(i>>A&0x1))
                while B > 0:
                    B -= 1
                    filewrite.write(', %d'%(BIT>>B&0x1))
                    list2.append('%d'%(BIT>>B&0x1))
                filewrite.write('\n')
                ws.append(list2)
    binfile.close()
    filewrite.close()
    wb.save('%s/%s.xlsx' % (filepath, shotname))
    print('%s finish' % file_out)

if __name__ == '__main__':
    process_list = []
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    for file in file_list:
        process = Process(target = get_fail_addr_data,args=(file,))
        process_list.append(process)
        process.start()
    for process in process_list:
        process.join()
