#!/usr/bin/env python3
"""
使用Streamlit实现同义词替换界面
优点：语法简单，生态成熟，部署容易
"""

import streamlit as st
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="同义词替换",
    page_icon="🔄",
    layout="wide"
)

# 主标题
st.title("🔄 同义词替换")

# 添加导航标签
tab1, tab2, tab3 = st.tabs(["📝 文本处理", "🔧 拒答设定", "📚 原文库结论查库"])

with tab1:
    st.header("Step 1: 输入文本")
    st.caption("请在下方文本框中输入需要测试的文本内容")
    
    # 文本输入区域
    input_text = st.text_area(
        "输入文本",
        height=150,
        placeholder="西门子的DTI怎么样"
    )
    
    # 处理按钮
    if st.button("🚀 开始处理 (Step1获取初步距离答案/友商以及UIH技术名)", type="primary"):
        if input_text:
            with st.spinner("正在处理..."):
                # 这里添加你的处理逻辑
                st.success("✅ Step 1 处理完成！")
                st.session_state['step1_completed'] = True
        else:
            st.error("❌ 请先输入文本内容")

with tab2:
    st.header("Step 2: 更新待定信息")
    st.caption("Step2.1 #根据友商技术在定义上的归属")
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 友商技术信息表")
        
        # 初始化数据
        if 'competitor_df' not in st.session_state:
            st.session_state.competitor_df = pd.DataFrame({
                'idx': [0],
                'competitor_name': ['西门子'],
                'competitor_product': ['DTI'],
                'uih_product': ['DTI'],
                'belong_to_uih': [False],
                'candidate_product': ['GE, 飞利浦']
            })
        
        # 可编辑表格
        edited_competitor_df = st.data_editor(
            st.session_state.competitor_df,
            num_rows="dynamic",
            use_container_width=True,
            key="competitor_table"
        )
        st.session_state.competitor_df = edited_competitor_df
    
    with col2:
        st.subheader("🏢 UIH技术信息表")
        
        # 初始化数据
        if 'uih_df' not in st.session_state:
            st.session_state.uih_df = pd.DataFrame({
                'idx': [0],
                'belong_to_which': ['DTI'],
                'corresponding_product': ['DTI'],
                'uih_product': [['UIH', 'DTI']],
                'candidate_product': [['GE']]
            })
        
        # 可编辑表格
        edited_uih_df = st.data_editor(
            st.session_state.uih_df,
            num_rows="dynamic",
            use_container_width=True,
            key="uih_table"
        )
        st.session_state.uih_df = edited_uih_df

with tab3:
    st.header("Step 3: 获取最终拒答策略")
    st.caption("基于前两步的选择，生成最终的拒答策略结果")
    
    # 显示处理进度
    if 'step1_completed' in st.session_state:
        st.success("✅ Step 1 已完成")
    else:
        st.warning("⏳ 请先完成 Step 1")
    
    # 最终处理按钮
    if st.button("🎯 开始处理 (Step3获取最终拒答策略)", type="primary"):
        with st.spinner("正在生成拒答策略..."):
            # 这里添加最终处理逻辑
            st.success("✅ 拒答策略生成完成！")
            
            # 显示结果
            st.subheader("📋 拒答结果")
            result_data = {
                'refuse_index': [3],
                'candidate_text': ['西门子的DTI怎么样'],
                'is_refuse': [True],
                'refuse_reason': [False],
                'refuse_tech': ['您好，您的提问涉及西门子的DTI技术，很抱歉无法为您提供咨询服务。作为上海联影医疗科技股份有限公司的人工智能助手，我的职责...']
            }
            
            result_df = pd.DataFrame(result_data)
            st.dataframe(result_df, use_container_width=True)

# 侧边栏信息
with st.sidebar:
    st.header("ℹ️ 使用说明")
    st.markdown("""
    1. **文本处理**: 输入需要测试的文本
    2. **拒答设定**: 配置友商和UIH技术信息
    3. **查库结论**: 获取最终的拒答策略
    """)
    
    st.header("📊 处理状态")
    if 'step1_completed' in st.session_state:
        st.success("Step 1 ✅")
    else:
        st.info("Step 1 ⏳")