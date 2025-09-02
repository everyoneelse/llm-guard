#!/usr/bin/env python3
"""
简化版NiceGUI实现 - 避免常见陷阱
"""

from nicegui import ui
import pandas as pd

# 页面标题
ui.label('同义词替换').style('font-size: 2em; font-weight: bold; text-align: center')

# Step 1
with ui.card().style('width: 100%; margin: 20px 0'):
    ui.label('Step 1: 输入文本').style('font-size: 1.5em; font-weight: bold')
    ui.label('请在下方文本框中输入需要测试的文本内容').style('color: gray')
    
    text_input = ui.textarea(placeholder='西门子的DTI怎么样').style('width: 100%; height: 150px')
    
    def process_step1():
        if text_input.value:
            ui.notify('Step 1 处理完成！', color='positive')
        else:
            ui.notify('请先输入文本', color='negative')
    
    ui.button('开始处理 (Step1)', on_click=process_step1).style('background: #4CAF50; color: white; padding: 10px 20px')

# Step 2
with ui.card().style('width: 100%; margin: 20px 0'):
    ui.label('Step 2: 更新待定信息').style('font-size: 1.5em; font-weight: bold')
    
    with ui.row().style('width: 100%'):
        with ui.column().style('width: 48%'):
            ui.label('友商技术信息表').style('font-weight: bold')
            
            # 简单的表格显示
            competitor_data = [
                ['0', '西门子', 'DTI', 'DTI', 'false', 'GE, 飞利浦']
            ]
            
            with ui.grid(columns=6).style('width: 100%'):
                # 表头
                ui.label('idx').style('font-weight: bold')
                ui.label('竞争对手').style('font-weight: bold')
                ui.label('竞争产品').style('font-weight: bold')
                ui.label('UIH产品').style('font-weight: bold')
                ui.label('是否拒答').style('font-weight: bold')
                ui.label('候选产品').style('font-weight: bold')
                
                # 数据行
                for row in competitor_data:
                    for cell in row:
                        ui.input(value=cell).style('width: 100%')
        
        with ui.column().style('width: 48%; margin-left: 4%'):
            ui.label('UIH技术信息表').style('font-weight: bold')
            
            uih_data = [
                ['0', 'DTI', 'DTI', '["UIH", "DTI"]', '["GE"]']
            ]
            
            with ui.grid(columns=5).style('width: 100%'):
                # 表头
                ui.label('idx').style('font-weight: bold')
                ui.label('属于哪个').style('font-weight: bold')
                ui.label('对应产品').style('font-weight: bold')
                ui.label('UIH产品').style('font-weight: bold')
                ui.label('候选产品').style('font-weight: bold')
                
                # 数据行
                for row in uih_data:
                    for cell in row:
                        ui.input(value=cell).style('width: 100%')

# Step 3
with ui.card().style('width: 100%; margin: 20px 0'):
    ui.label('Step 3: 获取最终拒答策略').style('font-size: 1.5em; font-weight: bold')
    ui.label('基于前两步的选择，生成最终的拒答策略结果').style('color: gray')
    
    def process_final():
        ui.notify('拒答策略生成完成！', color='positive')
        result_text.set_text('拒答策略：您好，您的提问涉及西门子的DTI技术，很抱歉无法为您提供咨询服务...')
    
    ui.button('开始处理 (Step3获取最终拒答策略)', on_click=process_final).style('background: #2196F3; color: white; padding: 10px 20px')
    
    result_text = ui.textarea(placeholder='结果将在这里显示...').style('width: 100%; height: 200px; margin-top: 10px')

# 启动应用
ui.run(port=8080, title='同义词替换工具')