'''
Author: czqczqzzzzzz(czq)
Email: tenchenzhengqing@qq.com
Date: 2024-11-28 09:12:30
LastEditors: by-czq
LastEditTime: 2024-12-27 09:15:26
FilePath: \boya_upload_test_file_sys\pyLib\handle_3fabs_revA.py
Description: v5A 处理fab厂WATER良率(.xlsx) 数据log(.csv/.WAT) 各自并生成HTML报告 已经支持SMIC/XMC/HLMC三家 支持横向对比汇总图表 支持凸显想要的图表 优化性能，上图坐标正确，但下图坐标需要看个位数，中间没有分bin，点击图例可以控制所有子图

Copyright (c) by czqczqzzzzzz(czq), All Rights Reserved.
'''
import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from io import BytesIO  # 用于读取 ZIP 文件中的内容
from fuzzywuzzy import fuzz
import numpy as np
import matplotlib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import plotly.subplots as sp
# 设置中文字体为 SimHei（黑体）或其他中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题




# 提取文件名（忽略路径和扩展名）
def extract_filename(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

# 提取文件名中的第二个 '-' 后的部分
def extract_second_part(filename):
    basename = os.path.basename(filename)  # 获取文件名（去掉路径）
    if '_' in basename:
        parts = basename.split('_')  # 按 '-' 分割文件名
    elif '-' in basename:
        parts = basename.split('-')
    if len(parts) > 2:
        return parts[2]  # 返回第二个 '-' 后的部分
    return ''  # 如果没有第二个 '-'，返回空字符串


# folder1_files是xlsx，folder2_files是CSV或WAT
def fuzzy_match(folder1_files,folder2_files):

    # 存储匹配结果
    matched_pairs = []
    
    # 遍历 folder1 和 folder2 的文件名组合，计算相似度
    # xlsx
    for file1 in folder1_files:
        candidates = []  # 用于存储所有候选文件及相似度

        # 提取 file1 中第二个 '-' 后的部分
        second_part_file1 = extract_filename(file1).split('_')[0]
        #print(f"second_part_file1{second_part_file1}")
        
        # CSV或WAT
        for file2 in folder2_files:
            similarity = fuzz.ratio(extract_filename(file1), extract_filename(file2))
            candidates.append((file2, similarity))

            # 检查 file1 中第二个 '-' 后的部分是否在 file2 文件名中
            #if second_part_file1 and second_part_file1 in file2:
                #print(f"  The part '{second_part_file1}' from {file1} exists in {file2}.")

        # 找到最高相似度
        highest_score = max(candidates, key=lambda x: x[1])[1]
        best_matches = [f for f, s in candidates if s == highest_score]

        # 如果有多个最佳匹配，按第一个 '-' 前的部分优先选择
        if len(best_matches) > 1:
            # 检查哪些文件包含第一个 '-' 前的部分
            matches_with_second_part = [f for f in best_matches if second_part_file1 in f]

            if len(matches_with_second_part) == 1:
                # 如果只有一个文件包含第二个 '-' 后的部分，则选择该文件
                best_match = matches_with_second_part[0]
                print(f"  Automatically selected {best_match} based on the part '{second_part_file1}'.")
            else:
                # 如果多个匹配，则提示人工选择
                print("  Multiple matches found with same similarity and part match.")
                print("  Please choose manually:")
                for idx, match in enumerate(best_matches):
                    print(f"  {idx+1}. {match}")

                user_choice = int(input("  Enter the number of the best match: "))
                best_match = best_matches[user_choice - 1]
        else:
            # 如果只有一个最佳匹配，则直接选择
            best_match = best_matches[0]

        # 记录最终匹配结果
        matched_pairs.append((file1, best_match, highest_score))

    # 输出最终匹配结果
    print("\nFinal Matched Pairs:")
    for file1, file2, score in matched_pairs:
        print(f"{file1} <-> {file2}: Similarity = {score}%")
    
    return matched_pairs

def save_plot_to_zip(fig, plot_filename, folder_path):
    # 将图表保存为 HTML（这里返回的是字符串）
    html_str = fig.to_html()

    # 将 HTML 字符串转换为字节流
    html_bytes = html_str.encode('utf-8')
    
    
    # 创建 figures 文件夹（如果不存在）
    figures_folder = os.path.join(folder_path, 'figures')

    if not os.path.exists(figures_folder):
        os.makedirs(figures_folder)

    # 将 HTML 文件保存到 figures 文件夹
    try:
        # 文件保存路径
        plot_file_path = os.path.join(figures_folder, f'{plot_filename}.html')

        # 将 HTML 内容写入文件
        with open(plot_file_path, 'wb') as f:
            f.write(html_bytes)
        
        print(f"Plot saved successfully as {plot_filename}.html in the 'figures' folder.")
    except Exception as e:
        print(f"Error while saving plot: {e}")



def cre_html(df_1,df_2,second_part_file1,folder_path,x_all_print):
    # 准备数据
    num_cols = len(df_2.groupby(df_2.columns[1]))  # 获取分组数目，作为列数
    height_val=1000  # 增加图形高度
    width_val = 1000 * ((num_cols//10)+1)
    # 创建子图布局
    if second_part_file1 == 'Combined Interactive Charts':       
                # 创建子图布局
        fig = make_subplots(
            rows=3,
            cols=num_cols,
            row_heights=[0.25, 0.01,0.74],  # 设置行高度比例
            vertical_spacing=0.001, #行间距
            horizontal_spacing=0.001,  # 控制水平间距
            specs = [
                [{"colspan": num_cols}] + [None] * (num_cols - 1),  # 上行跨所有列
                [{}] * num_cols,
                [{"colspan": num_cols}] + [None] * (num_cols - 1)   # 下行也跨所有列
            ],
            subplot_titles=["Main Line"] +  [f"{j}<br>wafer {int(i)}" for i, j in zip(df_1.iloc[:, 2], df_1.iloc[:, 0])] + [] #包含每个子图标题的列表
            #subplot_titles=["Main Line"] + [f"wafer {i+1}" for i in range(num_cols)] #包含每个子图标题的列表
        )
    else:
        # 创建子图布局
        fig = make_subplots(
            rows=3,
            cols=num_cols,
            row_heights=[0.25, 0.01,0.74],  # 设置行高度比例
            vertical_spacing=0.001, #行间距
            horizontal_spacing=0.001,  # 控制水平间距
            specs = [
                [{"colspan": num_cols}] + [None] * (num_cols - 1),  # 上行跨所有列
                [{}] * num_cols,
                [{"colspan": num_cols}] + [None] * (num_cols - 1)   # 下行也跨所有列
            ],
            subplot_titles=["Main Line"] + [f"wafer {int(i)}" for i in df_1.iloc[:, 2]] + [] #包含每个子图标题的列表
            #subplot_titles=["Main Line"] + [f"wafer {i+1}" for i in range(num_cols)] #包含每个子图标题的列表
        )
    # 绘制上方的折线图
    x_data = np.arange(1,len(df_1.iloc[:, 2])+1)
    y_data = df_1.iloc[:, 1]
    
    fig.add_trace(
        go.Scatter(
            x=x_data * 2 - 1,
            y=y_data,
            mode="lines+markers",
            marker=dict(color="blue"),
            name="Main Line",
        ),
        row=1,
        col=1
    )
    # 设置上方折线图的 X 轴刻度
    x_ticks = np.arange(0, 2 * len(x_data) + 2, 2)
    fig.update_xaxes(
        tickvals=x_ticks,
        ticktext=[str(x) for x in x_ticks],
        range=[0, x_ticks[-1]],
        row=1,
        col=1,
        showgrid=True,
        showticklabels=False  # 隐藏刻度标签
    )
    
    # 设置主图的 Y 轴范围，避免多余的间隙
    fig.update_yaxes(
        title_text="良率 %",
        range=[y_data.min()-0.1, y_data.max() + 0.2],  # 设置 y 轴
        row=1,
        col=1,
        showgrid=False
    )
    
    # 添加竖直网格线（竖线）
    for tick in x_ticks:
        fig.add_trace(
            go.Scatter(
                x=[tick, tick],  # 固定的 x 值，y 轴范围内的两个点
                y=[y_data.min()-0.1, y_data.max() + 0.2],  # y 值的范围
                mode="lines",
                line=dict(color="white", dash="solid", width=width_val*0.001),  # 设置竖线的样式
                showlegend=False
            ),
            row=1,
            col=1
        )
    color_index = 0
    # 创建一个字典，用于存储每个列的颜色（相同列使用相同颜色）
    color_dict = {}
    
    
    # 根据第二列对数据进行分组，并绘制每个分组的折线图
    #grouped = df_2.groupby(df_2.columns[1])

    # 找到第一列的唯一值并升序排序，生成字典
    unique_mapping = {val: idx for idx, val in enumerate(sorted(df_2[df_2.columns[1]].unique()))}
    
    # 打印生成的字典
    print("映射字典:", unique_mapping)
    
    # 按第一列升序排序
    group = df_2.sort_values(by=df_2.columns[1]).reset_index(drop=True)
    
    # 第二列的值更新：值 + 9 * 字典中对应编号
    group[group.columns[2]] = group[group.columns[2]] + group[group.columns[1]].map(unique_mapping) * 10
    
    # 按第二列升序排序
    group = group.sort_values(by=group.columns[2]).reset_index(drop=True)

    if x_all_print:
        # 设置 hovermode 为 x，使得鼠标悬停在某一点时显示所有线的值和图例
        fig.update_layout(
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor=None,  # 设置为 None 时，会自动继承线条颜色
                font_size=12,
                font_family="Arial",
                font_color="black"
            )
        )
            


    for j, col in enumerate(group.columns[3:]): 
        # 检查这个列的颜色是否已经在 color_dict 中
        if col not in color_dict:
            # 如果没有，生成一个新的随机颜色
            color_dict[col] = colors[color_index]
            #print(color_dict)
            color_index+=1
            #print(color_index)
    
        # 获取这个列的颜色
        color = color_dict[col]
    
        fig.add_trace(
            go.Scatter(
                x=group[group.columns[2]],
                y=group[col],
                mode="lines",
                marker=dict(color=color),
                name = f"{col}",
            ),
            row=3,
            col=1
        )
    
        # 设置上方折线图的 X 轴刻度
        x_ticks_low = np.arange(0, group.iloc[-1,2]+10, 10)
        fig.update_xaxes(
            tickvals=x_ticks_low,
            ticktext=[str(x) for x in x_ticks_low],
            range=[0, x_ticks_low[-1]],
            row=3,
            col=1,
            showgrid=False,
            showticklabels=False  # 隐藏刻度标签
        )
    
        # 设置每个河流图的 Y 轴范围
        fig.update_yaxes(
            title_text="值",
            range=[group.iloc[:, 3:].min().min() - 100, group.iloc[:, 3:].max().max() + 100],  # 根据数据的最小值和最大值调整范围
            row=3,
            col=1,
            showgrid=False
        )
    
        # 添加竖直网格线（竖线）
    for tick in x_ticks_low:
        fig.add_trace(
            go.Scatter(
                x=[tick, tick],  # 固定的 x 值，y 轴范围内的两个点
                y=[group.iloc[:, 3:].min().min() - 100, group.iloc[:, 3:].max().max() + 100],  # y 值的范围
                mode="lines",
                line=dict(color="white", dash="solid", width=width_val*0.001),  # 设置竖线的样式
                showlegend=False
            ),
            row=3,
            col=1
        )


    # 更新布局，增加合适的图形大小
    fig.update_layout(
        height=height_val,  # 增加图形高度
        width=width_val,  # 增加图形宽度
        #title_text="Plotly Subplots Example"
    )    
    
    save_plot_to_zip(fig,second_part_file1,folder_path)
    

def count_dashes(input_str):
    # 统计字符串中 '-' 的数量
    dash_count = input_str.count('_') + input_str.count('-')
    
    if dash_count == 2:
        print("字符串中有 2 个 '-'")
    elif dash_count == 3:
        print("字符串中有 3 个 '-'")
    else:
        print(f"字符串中有 {dash_count} 个 '-'")
    
    return dash_count



colors = [
    "#FF6347",  # 西红柿红
    "#FFD700",  # 金色
    "#ADFF2F",  # 绿黄色
    "#00FFFF",  # 青色
    "#8A2BE2",  # 蓝紫色
    "#FF1493",  # 深粉色
    "#00FF00",  # 绿色
    "#7FFF00",  # 春绿色
    "#0000FF",  # 蓝色
    "#FF00FF",  # 品红
    "#32CD32",  # 石灰绿
    "#800080",  # 紫色
    "#FFA500",  # 橙色
    "#FF4500",  # 橙红色
    "#00BFFF",  # 深天蓝
    "#DC143C",  # 猩红色
    "#F0E68C",  # 卡其色
    "#D2691E",  # 巧克力色
    "#4B0082",  # 靛蓝
    "#B22222",  # 火砖色
    "#8B0000",  # 暗红色
    "#A52A2A",  # 棕色
    "#006400",  # 深绿色
    "#FFD700",  # 金色
    "#4682B4",  # 钢蓝
    "#228B22",  # 森林绿
    "#C71585",  # 中紫红
    "#9932CC",  # 深紫色
    "#3CB371",  # 中海蓝
    "#FF8C00",  # 暗橙色
    "#C0C0C0",  # 银色
    "#DC143C",  # 猩红色
    "#FF4500",  # 橙红色
    "#32CD32",  # 石灰绿
    "#800080",  # 紫色
    "#008080",  # 蓝绿色
    "#6A5ACD",  # 灰蓝色
    "#8B4513",  # SaddleBrown
    "#B0E0E6",  # PowderBlue
    "#A9A9A9",  # 暗灰色
    "#800000",  # 棕色
    "#808000",  # 橄榄绿
    "#008000",  # 深绿色
    "#FF7F50",  # 珊瑚色
    "#F08080",  # 浅珊瑚色
    "#87CEEB",  # 天空蓝
    "#20B2AA",  # LightSeaGreen
    "#F4A460",  # 沙色
    "#FFDAB9",  # 杏仁色
    "#FF1493",  # 深粉色
    "#FF69B4",  # 热情粉色
    "#2E8B57",  # 海洋绿
    "#C71585",  # 中紫红
    "#FFB6C1",  # 浅粉色
    "#DDA0DD",  # 紫丁香色
    "#B0E0E6",  # PowderBlue
    "#48D1CC",  # MediumTurquoise
    "#98FB98",  # PaleGreen
    "#F5FFFA",  # 海洋白
    "#8B008B",  # 暗紫红色
    "#556B2F",  # 深橄榄绿
    "#FFD700",  # 金色
    "#FF6347",  # 西红柿红
    "#98FB98",  # PaleGreen
    "#A52A2A",  # 棕色
    "#800000",  # 棕色
    "#8A2BE2",  # 蓝紫色
    "#FF1493",  # 深粉色
    "#40E0D0",  # 宝石蓝
    "#FF4500",  # 橙红色
    "#D2691E",  # 巧克力色
    "#FF8C00",  # 暗橙色
    "#20B2AA",  # LightSeaGreen
    "#FFB6C1",  # 浅粉色
    "#808080",  # 灰色
    "#4B0082",  # 靛蓝
    "#D3D3D3",  # 浅灰色
    "#F08080",  # 浅珊瑚色
    "#FF00FF",  # 品红
    "#98FB98",  # PaleGreen
    "#6495ED",  # 玉石蓝
    "#7B68EE",  # 暗蓝紫色
    "#FF0000",  # 红色
    "#FFD700",  # 金色
    "#FF69B4",  # 热情粉色
    "#B22222",  # 火砖色
    "#C71585",  # 中紫红
    "#8A2BE2",  # 蓝紫色
    "#3CB371",  # 中海蓝
    "#20B2AA",  # LightSeaGreen
    "#6A5ACD",  # 灰蓝色
    "#A9A9A9",  # 暗灰色
    "#F0E68C",  # 卡其色
    "#D2691E",  # 巧克力色
    "#808000"  # 橄榄绿]
]




# 文件列表
list_1 = []  # 保存 .xlsx 文件
list_2 = []  # 保存 .csv 文件
list_3 = []  # 保存 .WAT文件

def select_folder():
    """通过 Tkinter 导入文件夹中的数据并分类到 list_1 和 list_2"""
    global list_1, list_2, list_3
    list_1.clear()
    list_2.clear()
    list_3.clear()
    

    # 打开文件夹选择对话框
    folder_path = filedialog.askdirectory(title="请选择一个文件夹")
    if folder_path:
        # 遍历文件夹中的所有文件并分类
        for file in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file)
            if os.path.isfile(full_path):
                if file.endswith('.xlsx'):
                    list_1.append(full_path)
                elif file.endswith('.csv'):
                    list_2.append(full_path)
                elif file.endswith('.WAT'):
                    list_3.append(full_path)
        
        print(f"Excel 文件列表 (.xlsx): {list_1}")
        print(f"CSV 文件列表 (.csv): {list_2}")
        print(f"WAT 文件列表(.WAT):{list_3}")
    else:
        print("未选择文件夹或文件夹为空")
    return folder_path



# 运行 Tkinter 文件选择过程
root = tk.Tk()
root.withdraw()  # 隐藏 Tkinter 主窗口
folder_path=select_folder()  # 选择文件夹

#不显示所有线条的图标
x_all_print = False
#显示所有线条的图标
#x_all_print = True


#判断三种文件类型，分别进行匹配
# 如果是csv
if list_2 and not list_3:
    df_i_index = 0
    matched_pairs=fuzzy_match(list_1,list_2)
    
    for file1, file2, score in matched_pairs:  
        
        df_i_index += 1
    
        # df_1为xlsx,df_2为csv
        # flie1为xlsx，file2为csx
        if count_dashes(file2) == 2:
            df_2 = pd.read_csv(file2, skiprows=2)
            df_2 = df_2.dropna(subset=[df_2.columns[1]])
            #second_part_file1 = extract_second_part(extract_filename(file2))
        elif count_dashes(file2) == 3:
            df_2 = pd.read_csv(file2, skiprows=14)
            df_2 = df_2.iloc[:, 1:]
            df_2 = df_2.dropna(subset=[df_2.columns[2]])
            df_2.iloc[:,3:] = df_2.iloc[:,3:].astype(float)
            df_2.iloc[:,1] = df_2.iloc[:,1].astype(int)
    
        
        df_1 = pd.read_excel(file1)
        
        df_1 = df_1[['Lot','Yield','Wafer']]
        df_1 = df_1.dropna(subset=[df_1.columns[0]])
        
        
        second_part_file1 = extract_second_part(extract_filename(file2))
        
        cre_html(df_1,df_2,second_part_file1,folder_path,x_all_print)
        
        if df_i_index == 1:
            df_1_all = df_1
            df_2_all = df_2
        elif df_i_index > 1:
            df_1['Wafer'] = df_1['Wafer'] + 25*(df_i_index-1)
            #df_2['Wafer'] = df_2['Wafer'] + 25*(df_i_index-1)
            df_2.iloc[:, 1] = df_2.iloc[:, 1] + 25 * (df_i_index - 1)
            
            
            df_1_all = pd.concat([df_1_all, df_1], axis=0, ignore_index=True)
            df_2_all = pd.concat([df_2_all, df_2], axis=0, ignore_index=True)

# 如果是WAT
elif not list_2 and list_3:
    df_i_index = 0
    matched_pairs=fuzzy_match(list_1,list_3)
    
    for file1, file2, score in matched_pairs: 
        
        df_i_index += 1
    
        # df_1为xlsx,df_2为WAT
        # flie1为xlsx，file2为WAT
        df_2 = pd.read_csv(file2, skiprows=13)
        df_2 = df_2.iloc[:, 1:]
        
        df_2 = df_2.dropna(subset=[df_2.columns[2]])
        df_2.iloc[:,3:] = df_2.iloc[:,3:].astype(float)
        df_2.iloc[:,1] = df_2.iloc[:,1].astype(int)
        
        df_1 = pd.read_excel(file1)
        
        df_1 = df_1[['Lot','Yield','Wafer']]
        df_1 = df_1.dropna(subset=[df_1.columns[0]])
        
        second_part_file1 = extract_second_part(extract_filename(file2))
        
        cre_html(df_1,df_2,second_part_file1,folder_path,x_all_print)
        
        if df_i_index == 1:
            df_1_all = df_1
            df_2_all = df_2
        elif df_i_index > 1:
            df_1['Wafer'] = df_1['Wafer'] + 25*(df_i_index-1)
            #df_2['Wafer'] = df_2['Wafer'] + 25*(df_i_index-1)
            df_2.iloc[:, 1] = df_2.iloc[:, 1] + 25 * (df_i_index - 1)
            
            df_1_all = pd.concat([df_1_all, df_1], axis=0, ignore_index=True)
            df_2_all = pd.concat([df_2_all, df_2], axis=0, ignore_index=True)
        

cre_html(df_1_all,df_2_all,'Combined Interactive Charts',folder_path,x_all_print)






