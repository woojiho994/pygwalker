import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer

# 设置页面配置
st.set_page_config(page_title="数据可视化平台", layout="wide")

# 添加数据处理选项
auto_convert = st.checkbox("自动处理数据类型", value=True, 
                          help="将所有文本列转为明确的字符串类型，避免大部分类型转换错误")
manual_convert = st.checkbox("手动控制数据类型转换", value=False, 
                           help="如果可视化错误，可以开启此选项手动选择列进行类型转换")

# 手动数据类型转换功能
def manual_type_conversion(dataframe):
    """让用户手动选择需要转换的列"""
    # 创建数据副本以避免修改原始数据
    df_converted = dataframe.copy()
    
    # 获取所有列名
    all_columns = df_converted.columns.tolist()
    
    # 让用户选择需要转换的列
    st.subheader("数据类型手动转换")
    
    # 字符串列转换
    string_cols = st.multiselect(
        "选择需要转换为字符串的列",
        options=all_columns,
        default=[]
    )
    
    # 数值列转换
    numeric_cols = st.multiselect(
        "选择需要转换为数值的列",
        options=all_columns,
        default=[]
    )
    
    # 转换为字符串
    for col in string_cols:
        df_converted[col] = df_converted[col].astype(str)
    
    # 转换为数值
    for col in numeric_cols:
        df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
        df_converted[col] = df_converted[col].fillna(0)
    
    return df_converted

# 显示数据类型信息
def show_data_types(df):
    """安全显示数据类型信息"""
    try:
        st.subheader("数据类型信息")
        
        # 创建一个简单的文本显示
        for col, dtype in df.dtypes.items():
            st.text(f"{col}: {dtype}")
    except Exception as e:
        st.warning(f"无法显示数据类型信息: {e}")

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
            
            # 显示数据类型信息
            show_data_types(df)
            
            # 自动处理数据类型
            if auto_convert:
                # 将所有对象类型列转为字符串
                object_cols = df.select_dtypes(include=['object']).columns
                if len(object_cols) > 0:
                    st.info(f"已将 {len(object_cols)} 个文本列自动转换为字符串类型")
                    for col in object_cols:
                        df[col] = df[col].astype(str)
            
            # 如果用户选择手动转换，则提供转换选项
            if manual_convert:
                df = manual_type_conversion(df)
        
        st.success("文件加载成功！")
    except Exception as e:
        st.error(f"加载文件时出错: {e}")

# 如果有数据，显示可视化
if df is not None:
    # 数据预览选项卡
    tab1, tab2 = st.tabs(["数据预览", "数据可视化"])
    
    with tab1:
        st.subheader("数据预览")
        # 显示原始数据
        try:
            st.dataframe(df.head(50))
        except Exception as e:
            st.warning(f"显示数据预览时出错: {e}")
            # 降级为HTML显示
            st.write("前10行数据:")
            st.write(df.head(10).to_html(), unsafe_allow_html=True)
        
    with tab2:
        st.subheader("数据可视化")
        try:
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
        except Exception as e:
            st.error(f"创建可视化时出错: {e}")
            st.info("如果出现数据类型错误，请尝试下列解决方案:")
            st.info("1. 确保'自动处理数据类型'选项已开启")
            st.info("2. 或使用'手动控制数据类型转换'选择特定列")
            st.code(str(e), language="python")
            
            # 提供一键修复按钮
            if st.button("应用紧急类型修复"):
                fixed_df = df.copy()
                for col in fixed_df.columns:
                    if fixed_df[col].dtype == 'object':
                        fixed_df[col] = fixed_df[col].astype(str)
                
                st.success("尝试使用修复后的数据进行可视化")
                try:
                    pyg_app = StreamlitRenderer(fixed_df)
                    pyg_app.explorer()
                except Exception as e2:
                    st.error(f"修复后仍然出错: {e2}")
else:
    st.info("请上传Excel文件以开始可视化") 