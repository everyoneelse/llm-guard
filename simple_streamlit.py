#!/usr/bin/env python3
"""
超简单的Streamlit实现 - 零学习成本
"""

import streamlit as st
import pandas as pd

# 页面配置
st.set_page_config(page_title="同义词替换", page_icon="🔄", layout="wide")

st.title("🔄 同义词替换")

# Step 1: 输入文本
st.header("Step 1: 输入文本")
st.write("请在下方文本框中输入需要测试的文本内容")

input_text = st.text_area("输入文本", height=150, placeholder="西门子的DTI怎么样")

if st.button("🚀 开始处理 (Step1)", type="primary"):
    if input_text:
        st.success("✅ Step 1 处理完成！")
        st.session_state['text_processed'] = True
    else:
        st.error("请先输入文本")

# Step 2: 更新待定信息
st.header("Step 2: 更新待定信息")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 友商技术信息表")
    
    # 初始化数据
    if 'competitor_data' not in st.session_state:
        st.session_state.competitor_data = pd.DataFrame({
            'idx': [0],
            'competitor_name': ['西门子'],
            'competitor_product': ['DTI'],
            'uih_product': ['DTI'],
            'belong_to_uih': [False],
            'candidate_product': ['GE, 飞利浦']
        })
    
    # 可编辑表格 - Streamlit的data_editor非常强大且易用
    st.session_state.competitor_data = st.data_editor(
        st.session_state.competitor_data,
        num_rows="dynamic",  # 允许添加/删除行
        use_container_width=True
    )

with col2:
    st.subheader("🏢 UIH技术信息表")
    
    if 'uih_data' not in st.session_state:
        st.session_state.uih_data = pd.DataFrame({
            'idx': [0],
            'belong_to_which': ['DTI'],
            'corresponding_product': ['DTI'],
            'uih_product': ['UIH, DTI'],
            'candidate_product': ['GE']
        })
    
    st.session_state.uih_data = st.data_editor(
        st.session_state.uih_data,
        num_rows="dynamic",
        use_container_width=True
    )

# Step 3: 获取最终结果
st.header("Step 3: 获取最终拒答策略")
st.write("基于前两步的选择，生成最终的拒答策略结果")

if st.button("🎯 开始处理 (Step3)", type="primary"):
    with st.spinner("正在生成拒答策略..."):
        # 模拟处理时间
        import time
        time.sleep(1)
        
        st.success("✅ 拒答策略生成完成！")
        
        # 显示结果表格
        result_data = pd.DataFrame({
            'refuse_index': [3],
            'candidate_text': ['西门子的DTI怎么样'],
            'is_refuse': [True],
            'refuse_reason': [False],
            'refuse_tech': ['您好，您的提问涉及西门子的DTI技术，很抱歉无法为您提供咨询服务...']
        })
        
        st.subheader("📋 拒答结果")
        st.dataframe(result_data, use_container_width=True)

# 侧边栏
with st.sidebar:
    st.header("ℹ️ 使用说明")
    st.markdown("""
    ### 操作步骤：
    1. **输入文本** - 在文本框中输入要测试的内容
    2. **编辑表格** - 双击表格单元格进行编辑
    3. **生成策略** - 点击按钮获取拒答策略
    
    ### 表格操作：
    - 双击单元格编辑
    - 点击 + 添加新行
    - 选中行后按Delete删除
    """)
    
    if 'text_processed' in st.session_state:
        st.success("Step 1 已完成 ✅")
    else:
        st.info("等待输入文本 ⏳")