import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer

# 设置页面配置
st.set_page_config(page_title="数据可视化平台", layout="wide")

# 添加选项允许用户控制数据处理
auto_clean = st.checkbox("自动尝试修复数据类型问题", value=False, 
                         help="尝试修复数据格式问题以适应可视化。注意：这可能会改变某些数据。")

# 添加数据类型处理功能
def clean_data(dataframe):
    """保留原始数据，仅处理特定列"""
    # 创建数据副本以避免修改原始数据
    df_clean = dataframe.copy()
    
    # 获取所有列名
    all_columns = df_clean.columns.tolist()
    
    # 让用户选择需要转换为数值的列
    st.subheader("数据类型转换")
    st.write("检测到部分列可能需要转换类型才能正确可视化。请选择需要转换为数值类型的列：")
    
    cols_to_convert = st.multiselect(
        "选择需要转换为数值的列",
        options=all_columns,
        default=[]
    )
    
    # 转换用户选择的列
    for col in cols_to_convert:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    return df_clean

# 主页面
st.title("Excel数据可视化平台")

# 上传Excel文件
uploaded_file = st.file_uploader("上传Excel文件", type=["xlsx", "xls"])

# 加载数据
df = None

if uploaded_file is not None:
    try:
        with st.spinner("正在加载Excel文件..."):
            df = pd.read_excel(uploaded_file)
            # 应用数据清理
            if auto_clean:
                df = clean_data(df)
        st.success("文件加载成功！")
    except Exception as e:
        st.error(f"加载文件时出错: {e}")

# 如果有数据，显示可视化
if df is not None:
    # 数据预览选项卡
    tab1, tab2 = st.tabs(["数据预览", "数据可视化"])
    
    with tab1:
        st.subheader("数据预览")
        st.dataframe(df)
        
        # 显示数据统计信息
        st.subheader("数据统计")
        st.write(df.describe())
        
    with tab2:
        st.subheader("数据可视化")
        # 创建PyGWalker应用
        pyg_app = StreamlitRenderer(df)
        pyg_app.explorer()
        
        # 添加导出说明
        with st.expander("如何保存和分享您的图表"):
            st.markdown("""
            1. 点击图表右上角的导出按钮
            2. 点击"复制代码"按钮
            3. 保存该代码，下次使用时可以直接粘贴以恢复您的图表
            """)
else:
    st.info("请上传Excel文件以开始可视化") 