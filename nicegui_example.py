#!/usr/bin/env python3
"""
使用NiceGUI实现同义词替换界面
优点：界面更现代化，组件更丰富
"""

from nicegui import ui, run
import pandas as pd

# 全局状态
state = {
    'input_text': '',
    'competitor_data': [],
    'uih_data': [],
    'final_result': ''
}

def create_main_interface():
    """创建主界面"""
    
    # 页面标题
    ui.label('同义词替换').classes('text-3xl font-bold text-center mb-8')
    
    # 使用卡片布局，更现代化
    with ui.card().classes('w-full max-w-6xl mx-auto'):
        
        # Step 1: 输入文本
        with ui.expansion('Step 1: 输入文本', icon='edit').classes('w-full'):
            ui.label('请在下方文本框中输入需要测试的文本内容').classes('text-gray-600 mb-2')
            
            text_area = ui.textarea(
                placeholder='在这里输入你的文本...'
            ).classes('w-full').style('min-height: 150px')
            
            def process_step1():
                state['input_text'] = text_area.value
                ui.notify('Step 1 处理完成！', type='positive')
                # 这里添加你的处理逻辑
                
            ui.button(
                '开始处理 (Step1获取初步距离答案/友商以及UIH技术名)', 
                on_click=process_step1
            ).classes('mt-4 bg-blue-500 text-white px-6 py-2 rounded')

        # Step 2: 更新待定信息
        with ui.expansion('Step 2: 更新待定信息', icon='table_chart').classes('w-full mt-4'):
            
            with ui.row().classes('w-full gap-4'):
                # 友商技术信息表
                with ui.column().classes('flex-1'):
                    ui.label('友商技术信息表').classes('text-lg font-semibold mb-2')
                    
                    # 创建可编辑表格
                    competitor_columns = [
                        {'name': 'idx', 'label': 'ID', 'field': 'idx', 'sortable': True},
                        {'name': 'competitor_name', 'label': '竞争对手名称', 'field': 'competitor_name'},
                        {'name': 'competitor_product', 'label': '竞争对手产品', 'field': 'competitor_product'},
                        {'name': 'uih_product', 'label': 'UIH产品', 'field': 'uih_product'},
                        {'name': 'belong_to_uih', 'label': '是否拒答', 'field': 'belong_to_uih'},
                        {'name': 'candidate_product', 'label': '候选产品', 'field': 'candidate_product'},
                    ]
                    
                    competitor_rows = [
                        {
                            'idx': 0,
                            'competitor_name': '西门子',
                            'competitor_product': 'DTI',
                            'uih_product': 'DTI',
                            'belong_to_uih': False,
                            'candidate_product': 'GE, 飞利浦'
                        }
                    ]
                    
                    competitor_table = ui.table(
                        columns=competitor_columns,
                        rows=competitor_rows,
                        row_key='idx'
                    ).classes('w-full')
                
                # UIH技术信息表  
                with ui.column().classes('flex-1'):
                    ui.label('UIH技术信息表').classes('text-lg font-semibold mb-2')
                    
                    uih_columns = [
                        {'name': 'idx', 'label': 'ID', 'field': 'idx'},
                        {'name': 'belong_to_which', 'label': '属于哪个', 'field': 'belong_to_which'},
                        {'name': 'corresponding_product', 'label': '对应产品', 'field': 'corresponding_product'},
                        {'name': 'uih_product', 'label': 'UIH产品', 'field': 'uih_product'},
                        {'name': 'candidate_product', 'label': '候选产品', 'field': 'candidate_product'},
                    ]
                    
                    uih_rows = [
                        {
                            'idx': 0,
                            'belong_to_which': 'DTI',
                            'corresponding_product': 'DTI',
                            'uih_product': ['UIH', 'DTI'],
                            'candidate_product': ['GE']
                        }
                    ]
                    
                    uih_table = ui.table(
                        columns=uih_columns,
                        rows=uih_rows,
                        row_key='idx'
                    ).classes('w-full')

        # Step 3: 获取最终结果
        with ui.expansion('Step 3: 获取最终拒答策略', icon='psychology').classes('w-full mt-4'):
            ui.label('基于前两步的选择，生成最终的拒答策略结果').classes('text-gray-600 mb-4')
            
            def process_final():
                ui.notify('正在生成拒答策略...', type='info')
                # 这里添加最终处理逻辑
                state['final_result'] = "拒答策略已生成"
                result_area.set_text(state['final_result'])
                
            ui.button(
                '开始处理 (Step3获取最终拒答策略)', 
                on_click=process_final
            ).classes('bg-green-500 text-white px-6 py-2 rounded mb-4')
            
            # 结果显示区域
            result_area = ui.textarea('结果将在这里显示...').classes('w-full').style('min-height: 200px')

if __name__ == '__main__':
    create_main_interface()
    ui.run(port=8080, title='同义词替换工具')