# -*- coding: utf-8 -*-
import os
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, colors, Alignment
from tkinter import filedialog
import tkinter as tk


def get_filePath_list(raw_path,file_list = []):
    for file in sorted(os.listdir(raw_path)):
        path = os.path.join(raw_path, file)
        if os.path.isdir(path):
            get_filePath_list(path,file_list)
        elif path.endswith('.csv'):
            file_list.append(path)
    return file_list

def get_csv_data(file):
    data_list = []
    time_list = []
    f = open(file,'rb')
    lines = f.readlines()
    data_flag = 0
    for line in lines:
        strs = line.decode('windows-1252')
        if 'Time,Ampl' in strs :
            data_flag = 1
            continue
        if data_flag :
            time_list.append(float(strs.split(',')[0]))
            data_list.append(float(strs.split(',')[1].replace('\r\n', '')))
    f.close()
    return time_list, data_list


def deal_with_data(time_list, data_list):
    end_data_list = []
    temp = []
    time = 0
    data = 0
    for i in range(len(data_list)) :
        time = time + time_list[i]
        data = data + data_list[i]
        if ((i+1)/1000) and ((i+1)%1000==0):
            temp.append(float(time/1000))
            temp.append(float(data/1000))
            end_data_list.append(temp)
            time = 0
            data = 0
            temp = []
    return end_data_list
    

def data_to_excel(file, data_list):
    file_name = file.split('\\')[-1]
    file_path = file.replace(file_name,'') + 'NEW_DATA'
    isExists=os.path.exists(file_path)
    if not isExists:
        os.makedirs(file_path) 
        print(file_path+' 创建成功')
    # 实例化
    wb = Workbook()
    # 激活 worksheet
    sheet1 = wb.active
    # 设立表头
    row0 = ['Time','Ampl']
    sheet1.append(row0)
    alignment = Alignment(horizontal='center', vertical='center')
    for i in range(len(data_list)):
        sheet1.append(data_list[i])
    dims = {}
    for row in sheet1.rows:
        for cell in row:
            cell.alignment = alignment
            #自动设置列宽
            if cell.value:
                """
                首先获取每个单元格中的长度；如果有换行则按单行的长度计算，先分割再计算；
                长度计算中：len('中文')>>>2, len('中文'.encode('utf-8'))>>>6，通过运算，将中文的字节数定义为2；
                字典存储每列的宽度：将cell每列中 列名作为键名，cell长度计算的最大长度作为键值。
                """
                len_cell = max([
                    (len(line.encode('utf-8')) - len(line)) / 2 + len(line)
                    for line in str(cell.value).split('\n')
                ])
                #dims[chr(64+cell.column)] = max((dims.get(chr(64+cell.column), 0), len(str(cell.value))))
                dims[cell.column_letter] = max(dims.get(cell.column_letter, 0),
                                               len_cell)
    for col, value in dims.items():
        """最后通过遍历存储每列的宽度的字典，来设置相关列的宽度"""
        sheet1.column_dimensions[
            col].width = value + 2 if value + 2 <= 50 else 50
    wb.save(file_path + '\\' + file_name.replace('.csv','.xls'))


def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    file_list = get_filePath_list(file_path)
    for file in file_list:
        print(file)
        time_list, data_list = get_csv_data(file)
        data_list = deal_with_data(time_list, data_list)
        data_to_excel(file, data_list)
    print("******************")
    print("******end!!!******")
    print("******************")


if __name__ == '__main__':
    main()