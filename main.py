import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import time
import base64
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize session state variables if they don't exist
if 'processed_dfs' not in st.session_state:
    st.session_state.processed_dfs = {}
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None

# Configure the Streamlit app
st.set_page_config(
    page_title="Advanced Data Sweeper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create a sidebar for navigation and settings
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/data-configuration.png", width=80)
    st.title("Data Sweeper Pro")
    
    # Theme selection with a more attractive UI
    st.subheader("🎨 App Settings")
    theme = st.radio(
        "Choose Theme:",
        ["Dark Mode", "Light Mode"],
        help="Select your preferred color theme for the application"
    )
    
    # Navigation menu
    selected = option_menu(
        "Main Menu",
        ["Home", "Data Cleaning", "Visualization", "Analysis", "Export", "Help"],
        icons=["house", "tools", "bar-chart", "calculator", "download", "question-circle"],
        menu_icon="cast",
        default_index=0,
    )

# Custom CSS for Dark & Light Mode
if theme == "Dark Mode":
    dark_css = """
        <style>
            .block-container { padding: 2rem 1.5rem; border-radius: 12px; background-color: #1E1E1E; color: white; }
            h1, h2, h3, h4, h5, h6 { color:#fff; }
            .stButton>button { border: none; border-radius: 8px; background-color: #0078D7; color: white; padding: 0.75rem 1.5rem; font-size: 1rem; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4); transition: all 0.3s ease; }
            .stButton>button:hover { background-color: #005a9e; cursor: pointer; transform: translateY(-2px); }
            .stDownloadButton>button { background-color: #28a745; color: white; }
            .stDownloadButton>button:hover { background-color: #218838; }
            .stDataFrame, .stTable { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); }
            .stRadio>label, .stCheckbox>label { color: white; font-weight: bold; }
            .stTextInput>div>div>input { color: white; background-color: #2D2D2D; border-radius: 8px; }
            .stSelectbox>div>div>select { color: white; background-color: #2D2D2D; border-radius: 8px; }
            .stMultiselect>div>div>div>span { color: white; background-color: #2D2D2D; border-radius: 8px; }
            .sidebar .block-container { background-color: #252525; }
            .css-1d391kg { background-color: #252525; }
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #2D2D2D;
                border-radius: 8px 8px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #0078D7;
                color: white;
            }
            .stAlert { border-radius: 8px; }
            .stProgress > div > div > div > div { background-color: #0078D7; }
        </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    light_css = """
        <style>
            .block-container { padding: 2rem 1.5rem; border-radius: 12px; background-color: #ffffff; color: black; }
            h1, h2, h3, h4, h5, h6 { color:#000; }
            .stButton>button { border: none; border-radius: 8px; background-color: #0078D7; color: white; padding: 0.75rem 1.5rem; font-size: 1rem; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); transition: all 0.3s ease; }
            .stButton>button:hover { background-color: #005a9e; cursor: pointer; transform: translateY(-2px); }
            .stDownloadButton>button { background-color: #28a745; color: white; }
            .stDownloadButton>button:hover { background-color: #218838; }
            .stDataFrame, .stTable { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
            .stRadio>label, .stCheckbox>label { color: black; font-weight: bold; }
            .stTextInput>div>div>input { color: black; background-color: #F0F2F6; border-radius: 8px; }
            .stSelectbox>div>div>select { color: black; background-color: #F0F2F6; border-radius: 8px; }
            .stMultiselect>div>div>div>span { color: black; background-color: #F0F2F6; border-radius: 8px; }
            .sidebar .block-container { background-color: #f0f2f6; }
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #F0F2F6;
                border-radius: 8px 8px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #0078D7;
                color: white;
            }
            .stAlert { border-radius: 8px; }
            .stProgress > div > div > div > div { background-color: #0078D7; }
        </style>
    """
    st.markdown(light_css, unsafe_allow_html=True)

# Helper functions
def get_csv_download_link(df, filename, link_text):
    """Generate a download link for a CSV file."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">{link_text}</a>'
    return href

def get_excel_download_link(df, filename, link_text):
    """Generate a download link for an Excel file."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">{link_text}</a>'
    return href

def get_json_download_link(df, filename, link_text):
    """Generate a download link for a JSON file."""
    json_str = df.to_json(orient='records')
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">{link_text}</a>'
    return href

def load_data(file):
    """Load data from uploaded file with progress bar."""
    file_extension = os.path.splitext(file.name)[-1].lower()
    
    with st.spinner(f"Loading {file.name}..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
            
        try:
            if file_extension == ".csv":
                df = pd.read_csv(file)
            elif file_extension == ".xlsx" or file_extension == ".xls":
                df = pd.read_excel(file)
            elif file_extension == ".json":
                df = pd.read_json(file)
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
                
            st.session_state.processed_dfs[file.name] = df
            st.session_state.current_df = df
            st.session_state.file_name = file.name
            return df
        except Exception as e:
            st.error(f"❌ Error processing {file.name}: {e}")
            return None
        finally:
            progress_bar.empty()

def generate_basic_stats(df):
    """Generate basic statistics for the dataframe."""
    stats = df.describe(include='all').transpose()
    stats['missing'] = df.isnull().sum()
    stats['missing_percent'] = (df.isnull().sum() / len(df)) * 100
    return stats

# Home page
if selected == "Home":
    st.title("📊 Advanced Data Sweeper Pro")
    st.markdown("""
    <div style='background-color: rgba(0, 120, 215, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3>Welcome to Data Sweeper Pro!</h3>
        <p>A powerful tool to transform, clean, analyze, and visualize your data with ease.</p>
        <ul>
            <li><strong>Data Cleaning:</strong> Remove duplicates, handle missing values, filter data, and more</li>
            <li><strong>Visualization:</strong> Create beautiful charts and graphs with just a few clicks</li>
            <li><strong>Analysis:</strong> Get insights from your data with statistical analysis</li>
            <li><strong>Export:</strong> Save your processed data in multiple formats</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # File Uploader
    uploaded_files = st.file_uploader(
        "📁 Upload your data files:",
        type=["csv", "xlsx", "xls", "json"],
        accept_multiple_files=True,
        help="Supported formats: CSV, Excel, and JSON"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            df = load_data(file)
            if df is not None:
                st.success(f"✅ Successfully loaded {file.name}")
                
                # File info card
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", df.shape[0])
                with col2:
                    st.metric("Columns", df.shape[1])
                with col3:
                    st.metric("File Size", f"{file.size / 1024:.2f} KB")
                
                # Data preview
                with st.expander("🔍 Preview Data", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                    
                # Data summary
                with st.expander("📊 Data Summary"):
                    st.dataframe(df.describe(include='all'), use_container_width=True)
                    
                # Column info
                with st.expander("📋 Column Information"):
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes,
                        'Non-Null Count': df.count(),
                        'Null Count': df.isnull().sum(),
                        'Unique Values': [df[col].nunique() for col in df.columns]
                    })
                    st.dataframe(col_info, use_container_width=True)
    else:
        # Sample data option
        st.info("👆 Upload your data files above or use sample data to get started!")
        if st.button("Load Sample Data"):
            sample_data = pd.DataFrame({
                'Name': ['John', 'Anna', 'Peter', 'Linda', 'Max'],
                'Age': [28, 34, 45, 32, 22],
                'City': ['New York', 'Paris', 'Berlin', 'London', 'Tokyo'],
                'Salary': [65000, 72000, 85000, 69000, 58000],
                'Experience': [3, 5, 8, 4, 1]
            })
            st.session_state.processed_dfs['sample_data.csv'] = sample_data
            st.session_state.current_df = sample_data
            st.session_state.file_name = 'sample_data.csv'
            st.success("✅ Sample data loaded successfully!")
            st.dataframe(sample_data, use_container_width=True)

# Data Cleaning page
elif selected == "Data Cleaning":
    st.title("🧹 Data Cleaning")
    
    if not st.session_state.processed_dfs:
        st.warning("⚠️ Please upload or load sample data first!")
    else:
        # File selector
        file_names = list(st.session_state.processed_dfs.keys())
        selected_file = st.selectbox("Select a file to clean:", file_names)
        df = st.session_state.processed_dfs[selected_file]
        st.session_state.current_df = df
        st.session_state.file_name = selected_file
        
        # Show current dataframe
        st.subheader("Current Data")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Cleaning options in tabs
        cleaning_tabs = st.tabs(["Basic Cleaning", "Missing Values", "Outliers", "Data Types", "Custom Operations"])
        
        # Basic Cleaning tab
        with cleaning_tabs[0]:
            st.subheader("Basic Cleaning Operations")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove Duplicates"):
                    initial_count = df.shape[0]
                    df = df.drop_duplicates()
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Removed {initial_count - df.shape[0]} duplicate rows.")
                    st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                if st.button("Remove Empty Rows"):
                    initial_count = df.shape[0]
                    df = df.dropna(how='all')
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Removed {initial_count - df.shape[0]} empty rows.")
                    st.dataframe(df.head(10), use_container_width=True)
            
            # Column operations
            st.subheader("Column Operations")
            col1, col2 = st.columns(2)
            
            with col1:
                columns_to_remove = st.multiselect("Select columns to remove:", df.columns)
                if columns_to_remove and st.button("Remove Selected Columns"):
                    df = df.drop(columns=columns_to_remove)
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Removed columns: {', '.join(columns_to_remove)}")
                    st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                rename_col = st.selectbox("Select column to rename:", df.columns)
                new_name = st.text_input("Enter new column name:")
                if new_name and st.button("Rename Column"):
                    df = df.rename(columns={rename_col: new_name})
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Renamed column '{rename_col}' to '{new_name}'")
                    st.dataframe(df.head(10), use_container_width=True)
        
        # Missing Values tab
        with cleaning_tabs[1]:
            st.subheader("Handle Missing Values")
            
            # Display missing values summary
            missing_data = pd.DataFrame({
                'Column': df.columns,
                'Missing Values': df.isnull().sum(),
                'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
            })
            missing_data = missing_data.sort_values('Missing Values', ascending=False)
            st.dataframe(missing_data, use_container_width=True)
            
            # Missing value handling options
            st.subheader("Fill Missing Values")
            col1, col2 = st.columns(2)
            
            with col1:
                fill_method = st.radio(
                    "Select fill method for numeric columns:",
                    ["Mean", "Median", "Mode", "Constant Value", "Forward Fill", "Backward Fill"]
                )
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                selected_numeric_cols = st.multiselect("Select numeric columns to fill:", numeric_cols)
                
                if selected_numeric_cols and st.button("Fill Numeric Missing Values"):
                    for col in selected_numeric_cols:
                        if fill_method == "Mean":
                            df[col] = df[col].fillna(df[col].mean())
                        elif fill_method == "Median":
                            df[col] = df[col].fillna(df[col].median())
                        elif fill_method == "Mode":
                            df[col] = df[col].fillna(df[col].mode()[0])
                        elif fill_method == "Constant Value":
                            value = st.number_input("Enter constant value:", value=0)
                            df[col] = df[col].fillna(value)
                        elif fill_method == "Forward Fill":
                            df[col] = df[col].ffill()
                        elif fill_method == "Backward Fill":
                            df[col] = df[col].bfill()
                    
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Filled missing values in selected numeric columns.")
                    st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                selected_cat_cols = st.multiselect("Select categorical columns to fill:", categorical_cols)
                cat_fill_value = st.text_input("Enter value to fill with (e.g., 'Unknown'):", "Unknown")
                
                if selected_cat_cols and st.button("Fill Categorical Missing Values"):
                    for col in selected_cat_cols:
                        df[col] = df[col].fillna(cat_fill_value)
                    
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Filled missing values in selected categorical columns with '{cat_fill_value}'.")
                    st.dataframe(df.head(10), use_container_width=True)
            
            # Drop rows with missing values
            if st.button("Drop Rows with Missing Values"):
                initial_count = df.shape[0]
                df = df.dropna()
                st.session_state.processed_dfs[selected_file] = df
                st.session_state.current_df = df
                st.success(f"✅ Dropped {initial_count - df.shape[0]} rows with missing values.")
                st.dataframe(df.head(10), use_container_width=True)
        
        # Outliers tab
        with cleaning_tabs[2]:
            st.subheader("Detect and Handle Outliers")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            selected_col = st.selectbox("Select column to check for outliers:", numeric_cols)
            
            if selected_col:
                # Display boxplot
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(x=df[selected_col], ax=ax)
                st.pyplot(fig)
                
                # Calculate IQR
                Q1 = df[selected_col].quantile(0.25)
                Q3 = df[selected_col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Display outlier info
                outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
                st.write(f"Potential outliers detected: {len(outliers)} rows")
                st.write(f"Lower bound: {lower_bound:.2f}, Upper bound: {upper_bound:.2f}")
                
                if len(outliers) > 0:
                    st.dataframe(outliers, use_container_width=True)
                    
                    # Outlier handling options
                    outlier_action = st.radio(
                        "Select action for outliers:",
                        ["Remove outliers", "Cap outliers", "Replace with mean/median"]
                    )
                    
                    if st.button("Handle Outliers"):
                        if outlier_action == "Remove outliers":
                            df = df[(df[selected_col] >= lower_bound) & (df[selected_col] <= upper_bound)]
                            st.success(f"✅ Removed {len(outliers)} outlier rows.")
                        
                        elif outlier_action == "Cap outliers":
                            df[selected_col] = df[selected_col].clip(lower=lower_bound, upper=upper_bound)
                            st.success(f"✅ Capped outliers to range [{lower_bound:.2f}, {upper_bound:.2f}].")
                        
                        elif outlier_action == "Replace with mean/median":
                            replacement = st.radio("Replace with:", ["Mean", "Median"])
                            replacement_value = df[selected_col].mean() if replacement == "Mean" else df[selected_col].median()
                            
                            mask = (df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)
                            df.loc[mask, selected_col] = replacement_value
                            st.success(f"✅ Replaced {len(outliers)} outliers with {replacement.lower()} ({replacement_value:.2f}).")
                        
                        st.session_state.processed_dfs[selected_file] = df
                        st.session_state.current_df = df
                        
                        # Show updated boxplot
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.boxplot(x=df[selected_col], ax=ax)
                        st.pyplot(fig)
                        
                        st.dataframe(df.head(10), use_container_width=True)
        
        # Data Types tab
        with cleaning_tabs[3]:
            st.subheader("Change Data Types")
            
            # Display current data types
            dtypes_df = pd.DataFrame({
                'Column': df.columns,
                'Current Type': df.dtypes
            })
            st.dataframe(dtypes_df, use_container_width=True)
            
            # Change data type form
            col_to_change = st.selectbox("Select column to change type:", df.columns)
            new_type = st.selectbox("Select new data type:", ["int", "float", "str", "datetime", "category", "bool"])
            
            if st.button("Change Data Type"):
                try:
                    if new_type == "int":
                        df[col_to_change] = df[col_to_change].astype(int)
                    elif new_type == "float":
                        df[col_to_change] = df[col_to_change].astype(float)
                    elif new_type == "str":
                        df[col_to_change] = df[col_to_change].astype(str)
                    elif new_type == "datetime":
                        df[col_to_change] = pd.to_datetime(df[col_to_change])
                    elif new_type == "category":
                        df[col_to_change] = df[col_to_change].astype('category')
                    elif new_type == "bool":
                        df[col_to_change] = df[col_to_change].astype(bool)
                    
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Changed '{col_to_change}' to type {new_type}.")
                    
                    # Display updated data types
                    dtypes_df = pd.DataFrame({
                        'Column': df.columns,
                        'Current Type': df.dtypes
                    })
                    st.dataframe(dtypes_df, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error changing data type: {e}")
        
        # Custom Operations tab
        with cleaning_tabs[4]:
            st.subheader("Custom Operations")
            
            # Create new column
            st.write("Create a new column based on existing columns")
            new_col_name = st.text_input("New column name:")
            expression = st.text_area("Enter Python expression (use 'df' to reference the dataframe):", "df['column1'] + df['column2']")
            
            if new_col_name and expression and st.button("Create New Column"):
                try:
                    df[new_col_name] = eval(expression)
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Created new column '{new_col_name}'.")
                    st.dataframe(df.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error creating column: {e}")
            
            # Apply function to column
            st.write("Apply function to column")
            col_to_transform = st.selectbox("Select column to transform:", df.columns)
            transform_options = ["Uppercase", "Lowercase", "Title Case", "Round", "Absolute Value", "Log", "Square Root", "Custom Lambda"]
            transform_type = st.selectbox("Select transformation:", transform_options)
            
            if st.button("Apply Transformation"):
                try:
                    if transform_type == "Uppercase":
                        df[col_to_transform] = df[col_to_transform].astype(str).str.upper()
                    elif transform_type == "Lowercase":
                        df[col_to_transform] = df[col_to_transform].astype(str).str.lower()
                    elif transform_type == "Title Case":
                        df[col_to_transform] = df[col_to_transform].astype(str).str.title()
                    elif transform_type == "Round":
                        decimals = st.number_input("Decimal places:", min_value=0, max_value=10, value=2)
                        df[col_to_transform] = df[col_to_transform].round(decimals)
                    elif transform_type == "Absolute Value":
                        df[col_to_transform] = df[col_to_transform].abs()
                    elif transform_type == "Log":
                        df[col_to_transform] = np.log(df[col_to_transform])
                    elif transform_type == "Square Root":
                        df[col_to_transform] = np.sqrt(df[col_to_transform])
                    elif transform_type == "Custom Lambda":
                        lambda_expr = st.text_input("Enter lambda expression (e.g., 'lambda x: x + 10'):")
                        df[col_to_transform] = df[col_to_transform].apply(eval(lambda_expr))
                    
                    st.session_state.processed_dfs[selected_file] = df
                    st.session_state.current_df = df
                    st.success(f"✅ Applied {transform_type} to '{col_to_transform}'.")
                    st.dataframe(df.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error applying transformation: {e}")

# Visualization page
elif selected == "Visualization":
    st.title("📈 Data Visualization")
    
    if not st.session_state.processed_dfs:
        st.warning("⚠️ Please upload or load sample data first!")
    else:
        # File selector
        file_names = list(st.session_state.processed_dfs.keys())
        selected_file = st.selectbox("Select a file to visualize:", file_names)
        df = st.session_state.processed_dfs[selected_file]
        
        # Visualization options in tabs
        viz_tabs = st.tabs(["Basic Charts", "Statistical Plots", "Interactive Plots", "Custom Visualization"])
        
        # Basic Charts tab
        with viz_tabs[0]:
            st.subheader("Basic Charts")
            
            chart_type = st.selectbox(
                "Select chart type:",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"]
            )
            
            if chart_type == "Bar Chart":
                x_axis = st.selectbox("Select X-axis column:", df.columns)
                y_axis = st.selectbox("Select Y-axis column:", df.select_dtypes(include=['number']).columns)
                
                orientation = st.radio("Orientation:", ["Vertical", "Horizontal"])
                
                if st.button("Generate Bar Chart"):
                    fig = px.bar(
                        df, 
                        x=x_axis if orientation == "Vertical" else y_axis,
                        y=y_axis if orientation == "Vertical" else x_axis,
                        title=f"{y_axis} by {x_axis}",
                        orientation='v' if orientation == "Vertical" else 'h',
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Line Chart":
                x_axis = st.selectbox("Select X-axis column:", df.columns)
                y_axes = st.multiselect("Select Y-axis column(s):", df.select_dtypes(include=['number']).columns)
                
                if y_axes and st.button("Generate Line Chart"):
                    fig = px.line(
                        df, 
                        x=x_axis, 
                        y=y_axes,
                        title=f"Line Chart: {', '.join(y_axes)} over {x_axis}",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Scatter Plot":
                x_axis = st.selectbox("Select X-axis column:", df.select_dtypes(include=['number']).columns)
                y_axis = st.selectbox("Select Y-axis column:", df.select_dtypes(include=['number']).columns, index=min(1, len(df.select_dtypes(include=['number']).columns)-1))
                color_by = st.selectbox("Color by (optional):", ["None"] + df.columns.tolist())
                size_by = st.selectbox("Size by (optional):", ["None"] + df.select_dtypes(include=['number']).columns.tolist())
                
                if st.button("Generate Scatter Plot"):
                    fig = px.scatter(
                        df, 
                        x=x_axis, 
                        y=y_axis,
                        color=None if color_by == "None" else color_by,
                        size=None if size_by == "None" else size_by,
                        title=f"Scatter Plot: {y_axis} vs {x_axis}",
                        hover_data=df.columns
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Pie Chart":
                labels = st.selectbox("Select labels column:", df.columns)
                values = st.selectbox("Select values column:", df.select_dtypes(include=['number']).columns)
                
                if st.button("Generate Pie Chart"):
                    fig = px.pie(
                        df, 
                        names=labels, 
                        values=values,
                        title=f"Pie Chart: {values} by {labels}",
                        hole=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Histogram":
                column = st.selectbox("Select column for histogram:", df.select_dtypes(include=['number']).columns)
                bins = st.slider("Number of bins:", min_value=5, max_value=100, value=20)
                
                if st.button("Generate Histogram"):
                    fig = px.histogram(
                        df, 
                        x=column,
                        nbins=bins,
                        title=f"Histogram of {column}",
                        marginal="box"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Box Plot":
                y_axis = st.selectbox("Select column for box plot:", df.select_dtypes(include=['number']).columns)
                x_axis = st.selectbox("Group by (optional):", ["None"] + df.columns.tolist())
                
                if st.button("Generate Box Plot"):
                    fig = px.box(
                        df, 
                        y=y_axis,
                        x=None if x_axis == "None" else x_axis,
                        title=f"Box Plot of {y_axis}" + (f" grouped by {x_axis}" if x_axis != "None" else ""),
                        points="all"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Statistical Plots tab
        with viz_tabs[1]:
            st.subheader("Statistical Plots")
            
            stat_plot_type = st.selectbox(
                "Select statistical plot type:",
                ["Correlation Heatmap", "Pair Plot", "Distribution Plot", "Violin Plot"]
            )
            
            if stat_plot_type == "Correlation Heatmap":
                numeric_df = df.select_dtypes(include=['number'])
                
                if numeric_df.shape[1] < 2:
                    st.warning("⚠️ Need at least 2 numeric columns for correlation analysis.")
                else:
                    if st.button("Generate Correlation Heatmap"):
                        corr = numeric_df.corr()
                        fig = px.imshow(
                            corr,
                            text_auto=True,
                            color_continuous_scale='RdBu_r',
                            title="Correlation Heatmap"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif stat_plot_type == "Pair Plot":
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                selected_cols = st.multiselect("Select columns for pair plot (2-5 recommended):", numeric_cols, default=numeric_cols[:min(4, len(numeric_cols))])
                color_by = st.selectbox("Color by (optional):", ["None"] + df.columns.tolist())
                
                if len(selected_cols) < 2:
                    st.warning("⚠️ Please select at least 2 columns.")
                elif len(selected_cols) > 5:
                    st.warning("⚠️ Too many columns may make the plot cluttered. Consider selecting fewer.")
                else:
                    if st.button("Generate Pair Plot"):
                        fig = px.scatter_matrix(
                            df,
                            dimensions=selected_cols,
                            color=None if color_by == "None" else color_by,
                            title="Pair Plot"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif stat_plot_type == "Distribution Plot":
                column = st.selectbox("Select column for distribution:", df.select_dtypes(include=['number']).columns)
                
                if st.button("Generate Distribution Plot"):
                    fig = px.histogram(
                        df,
                        x=column,
                        marginal="box",
                        title=f"Distribution of {column}",
                        histnorm="probability density",
                        color_discrete_sequence=['#0078D7']
                    )
                    
                    # Add KDE curve
                    kde = sns.kdeplot(df[column].dropna())
                    line_data = kde.get_lines()[0].get_data()
                    fig.add_scatter(x=line_data[0], y=line_data[1], mode='lines', name='KDE', line=dict(color='red'))
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            elif stat_plot_type == "Violin Plot":
                y_axis = st.selectbox("Select column for violin plot:", df.select_dtypes(include=['number']).columns)
                x_axis = st.selectbox("Group by (optional):", ["None"] + df.columns.tolist())
                
                if st.button("Generate Violin Plot"):
                    fig = px.violin(
                        df,
                        y=y_axis,
                        x=None if x_axis == "None" else x_axis,
                        box=True,
                        points="all",
                        title=f"Violin Plot of {y_axis}" + (f" grouped by {x_axis}" if x_axis != "None" else "")
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Interactive Plots tab
        with viz_tabs[2]:
            st.subheader("Interactive Plots")
            
            interactive_plot_type = st.selectbox(
                "Select interactive plot type:",
                ["3D Scatter", "Bubble Chart", "Time Series", "Animated Chart"]
            )
            
            if interactive_plot_type == "3D Scatter":
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_cols) < 3:
                    st.warning("⚠️ Need at least 3 numeric columns for 3D scatter plot.")
                else:
                    x_axis = st.selectbox("Select X-axis column:", numeric_cols, index=0)
                    y_axis = st.selectbox("Select Y-axis column:", numeric_cols, index=min(1, len(numeric_cols)-1))
                    z_axis = st.selectbox("Select Z-axis column:", numeric_cols, index=min(2, len(numeric_cols)-1))
                    color_by = st.selectbox("Color by (optional):", ["None"] + df.columns.tolist())
                    
                    if st.button("Generate 3D Scatter Plot"):
                        fig = px.scatter_3d(
                            df,
                            x=x_axis,
                            y=y_axis,
                            z=z_axis,
                            color=None if color_by == "None" else color_by,
                            title=f"3D Scatter Plot: {x_axis}, {y_axis}, {z_axis}",
                            opacity=0.7
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif interactive_plot_type == "Bubble Chart":
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_cols) < 3:
                    st.warning("⚠️ Need at least 3 numeric columns for bubble chart.")
                else:
                    x_axis = st.selectbox("Select X-axis column:", numeric_cols, index=0)
                    y_axis = st.selectbox("Select Y-axis column:", numeric_cols, index=min(1, len(numeric_cols)-1))
                    size_by = st.selectbox("Size by:", numeric_cols, index=min(2, len(numeric_cols)-1))
                    color_by = st.selectbox("Color by (optional):", ["None"] + df.columns.tolist())
                    
                    if st.button("Generate Bubble Chart"):
                        fig = px.scatter(
                            df,
                            x=x_axis,
                            y=y_axis,
                            size=size_by,
                            color=None if color_by == "None" else color_by,
                            title=f"Bubble Chart: {y_axis} vs {x_axis} (size: {size_by})",
                            hover_data=df.columns
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif interactive_plot_type == "Time Series":
                # Check if there are datetime columns
                date_cols = []
                for col in df.columns:
                    try:
                        pd.to_datetime(df[col])
                        date_cols.append(col)
                    except:
                        pass
                
                if not date_cols:
                    st.warning("⚠️ No datetime columns detected. Please convert a column to datetime first.")
                else:
                    date_col = st.selectbox("Select date/time column:", date_cols)
                    value_cols = st.multiselect("Select value column(s):", df.select_dtypes(include=['number']).columns)
                    
                    if value_cols and st.button("Generate Time Series"):
                        # Ensure date column is datetime
                        plot_df = df.copy()
                        plot_df[date_col] = pd.to_datetime(plot_df[date_col])
                        plot_df = plot_df.sort_values(by=date_col)
                        
                        fig = px.line(
                            plot_df,
                            x=date_col,
                            y=value_cols,
                            title=f"Time Series: {', '.join(value_cols)} over time",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif interactive_plot_type == "Animated Chart":
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                if len(numeric_cols) < 2 or not categorical_cols:
                    st.warning("⚠️ Need at least 2 numeric columns and 1 categorical column for animated chart.")
                else:
                    x_axis = st.selectbox("Select X-axis column:", numeric_cols, index=0)
                    y_axis = st.selectbox("Select Y-axis column:", numeric_cols, index=min(1, len(numeric_cols)-1))
                    size_by = st.selectbox("Size by (optional):", ["None"] + numeric_cols)
                    color_by = st.selectbox("Color by:", categorical_cols)
                    animation_frame = st.selectbox("Animate by:", categorical_cols)
                    
                    if st.button("Generate Animated Chart"):
                        fig = px.scatter(
                            df,
                            x=x_axis,
                            y=y_axis,
                            size=None if size_by == "None" else size_by,
                            color=color_by,
                            animation_frame=animation_frame,
                            title=f"Animated Chart: {y_axis} vs {x_axis} by {animation_frame}",
                            hover_data=df.columns
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        # Custom Visualization tab
        with viz_tabs[3]:
            st.subheader("Custom Visualization")
            
            st.write("Create a custom visualization using Plotly Express")
            
            plot_type = st.selectbox(
                "Select plot type:",
                ["Scatter", "Line", "Bar", "Histogram", "Box", "Violin", "Pie", "Sunburst", "Treemap"]
            )
            
            # Common parameters for all plot types
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis (or values):", df.columns)
                color_col = st.selectbox("Color by (optional):", ["None"] + df.columns.tolist())
                title = st.text_input("Plot title:", f"Custom {plot_type} Plot")
            
            with col2:
                y_col = st.selectbox("Y-axis (optional):", ["None"] + df.columns.tolist())
                hover_data = st.multiselect("Hover data (optional):", df.columns)
                
            # Plot-specific parameters
            if plot_type in ["Scatter", "Line"]:
                size_col = st.selectbox("Size by (optional):", ["None"] + df.select_dtypes(include=['number']).columns.tolist())
                markers = st.checkbox("Show markers", value=True)
            
            elif plot_type in ["Histogram", "Box", "Violin"]:
                marginal = st.selectbox("Marginal plot:", ["None", "box", "violin", "rug"])
            
            elif plot_type in ["Sunburst", "Treemap"]:
                path = st.multiselect("Path (hierarchy):", df.columns)
            
            # Generate plot button
            if st.button("Generate Custom Plot"):
                try:
                    if plot_type == "Scatter":
                        fig = px.scatter(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            size=None if size_col == "None" else size_col,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Line":
                        fig = px.line(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            markers=markers,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Bar":
                        fig = px.bar(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Histogram":
                        fig = px.histogram(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            marginal=None if marginal == "None" else marginal,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Box":
                        fig = px.box(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Violin":
                        fig = px.violin(
                            df,
                            x=x_col,
                            y=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            box=True,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Pie":
                        fig = px.pie(
                            df,
                            names=x_col,
                            values=None if y_col == "None" else y_col,
                            color=None if color_col == "None" else color_col,
                            title=title,
                            hover_data=hover_data if hover_data else None
                        )
                    
                    elif plot_type == "Sunburst":
                        if not path:
                            st.error("❌ Please select at least one column for the path.")
                        else:
                            fig = px.sunburst(
                                df,
                                path=path,
                                values=None if y_col == "None" else y_col,
                                color=None if color_col == "None" else color_col,
                                title=title,
                                hover_data=hover_data if hover_data else None
                            )
                    
                    elif plot_type == "Treemap":
                        if not path:
                            st.error("❌ Please select at least one column for the path.")
                        else:
                            fig = px.treemap(
                                df,
                                path=path,
                                values=None if y_col == "None" else y_col,
                                color=None if color_col == "None" else color_col,
                                title=title,
                                hover_data=hover_data if hover_data else None
                            )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Option to download the plot
                    st.download_button(
                        label="Download Plot as HTML",
                        data=fig.to_html(),
                        file_name=f"{title.replace(' ', '_')}.html",
                        mime="text/html"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error generating plot: {e}")

# Analysis page
elif selected == "Analysis":
    st.title("🔍 Data Analysis")
    
    if not st.session_state.processed_dfs:
        st.warning("⚠️ Please upload or load sample data first!")
    else:
        # File selector
        file_names = list(st.session_state.processed_dfs.keys())
        selected_file = st.selectbox("Select a file to analyze:", file_names)
        df = st.session_state.processed_dfs[selected_file]
        
        # Analysis options in tabs
        analysis_tabs = st.tabs(["Summary Statistics", "Data Profiling", "Correlation Analysis", "Group Analysis"])
        
        # Summary Statistics tab
        with analysis_tabs[0]:
            st.subheader("Summary Statistics")
            
            # Display basic statistics
            st.write("Basic Statistics")
            st.dataframe(df.describe(include='all'), use_container_width=True)
            
            # Column-specific statistics
            st.write("Column-specific Statistics")
            selected_col = st.selectbox("Select column for detailed statistics:", df.columns)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"Statistics for '{selected_col}':")
                if df[selected_col].dtype.kind in 'ifc':  # numeric
                    stats = {
                        "Mean": df[selected_col].mean(),
                        "Median": df[selected_col].median(),
                        "Std Dev": df[selected_col].std(),
                        "Min": df[selected_col].min(),
                        "Max": df[selected_col].max(),
                        "Range": df[selected_col].max() - df[selected_col].min(),
                        "Skewness": df[selected_col].skew(),
                        "Kurtosis": df[selected_col].kurtosis(),
                        "Missing Values": df[selected_col].isnull().sum(),
                        "Missing %": df[selected_col].isnull().mean() * 100
                    }
                else:  # categorical
                    stats = {
                        "Unique Values": df[selected_col].nunique(),
                        "Most Common": df[selected_col].mode()[0],
                        "Most Common Count": df[selected_col].value_counts().iloc[0],
                        "Most Common %": df[selected_col].value_counts(normalize=True).iloc[0] * 100,
                        "Missing Values": df[selected_col].isnull().sum(),
                        "Missing %": df[selected_col].isnull().mean() * 100
                    }
                
                for stat, value in stats.items():
                    st.write(f"**{stat}:** {value:.4f}" if isinstance(value, float) else f"**{stat}:** {value}")
            
            with col2:
                if df[selected_col].dtype.kind in 'ifc':  # numeric
                    fig = px.histogram(
                        df,
                        x=selected_col,
                        title=f"Distribution of {selected_col}",
                        marginal="box"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:  # categorical
                    top_n = min(10, df[selected_col].nunique())
                    value_counts = df[selected_col].value_counts().head(top_n)
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"Top {top_n} values for {selected_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Data Profiling tab
        with analysis_tabs[1]:
            st.subheader("Data Profiling")
            
            if st.button("Generate Basic Statistics"):
                stats = generate_basic_stats(df)
                st.write(stats)
        
        # Correlation Analysis tab
        with analysis_tabs[2]:
            st.subheader("Correlation Analysis")
            
            numeric_df = df.select_dtypes(include=['number'])
            
            if numeric_df.shape[1] < 2:
                st.warning("⚠️ Need at least 2 numeric columns for correlation analysis.")
            else:
                # Correlation method
                corr_method = st.radio(
                    "Correlation method:",
                    ["Pearson", "Spearman", "Kendall"],
                    help="Pearson: linear correlation, Spearman: rank correlation, Kendall: ordinal association"
                )
                
                # Generate correlation matrix
                corr = numeric_df.corr(method=corr_method.lower())
                
                # Display correlation heatmap
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale='RdBu_r',
                    title=f"{corr_method} Correlation Heatmap"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display top correlations
                st.subheader("Top Correlations")
                
                # Create a DataFrame with all pairwise correlations
                corr_pairs = corr.unstack().reset_index()
                corr_pairs.columns = ['Variable 1', 'Variable 2', 'Correlation']
                
                # Remove self-correlations and duplicates
                corr_pairs = corr_pairs[corr_pairs['Variable 1'] != corr_pairs['Variable 2']]
                corr_pairs['Pair'] = corr_pairs.apply(lambda row: tuple(sorted([row['Variable 1'], row['Variable 2']])), axis=1)
                corr_pairs = corr_pairs.drop_duplicates(subset=['Pair'])
                corr_pairs = corr_pairs.drop('Pair', axis=1)
                
                # Sort by absolute correlation
                corr_pairs['Abs Correlation'] = corr_pairs['Correlation'].abs()
                corr_pairs = corr_pairs.sort_values('Abs Correlation', ascending=False).drop('Abs Correlation', axis=1)
                
                st.dataframe(corr_pairs.head(10), use_container_width=True)
                
                # Scatter plot for selected variables
                st.subheader("Correlation Scatter Plot")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    var1 = st.selectbox("Select first variable:", numeric_df.columns)
                
                with col2:
                    var2 = st.selectbox("Select second variable:", numeric_df.columns, index=min(1, len(numeric_df.columns)-1))
                
                fig = px.scatter(
                    df,
                    x=var1,
                    y=var2,
                    trendline="ols",
                    title=f"Scatter Plot: {var2} vs {var1}",
                    trendline_color_override="red"
                )
                
                # Add correlation coefficient to the title
                corr_val = df[var1].corr(df[var2], method=corr_method.lower())
                fig.update_layout(title=f"Scatter Plot: {var2} vs {var1} (Correlation: {corr_val:.4f})")
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Group Analysis tab
        with analysis_tabs[3]:
            st.subheader("Group Analysis")
            
            # Select grouping column
            group_col = st.selectbox("Select column to group by:", df.columns)
            
            # Select aggregation columns
            agg_cols = st.multiselect(
                "Select columns to aggregate:",
                df.select_dtypes(include=['number']).columns
            )
            
            if agg_cols:
                # Select aggregation functions
                agg_funcs = st.multiselect(
                    "Select aggregation functions:",
                    ["Mean", "Median", "Sum", "Min", "Max", "Count", "Std Dev"],
                    default=["Mean"]
                )
                
                if agg_funcs and st.button("Perform Group Analysis"):
                    # Map selected functions to pandas aggregation functions
                    func_map = {
                        "Mean": "mean",
                        "Median": "median",
                        "Sum": "sum",
                        "Min": "min",
                        "Max": "max",
                        "Count": "count",
                        "Std Dev": "std"
                    }
                    
                    selected_funcs = [func_map[func] for func in agg_funcs]
                    
                    # Create aggregation dictionary
                    agg_dict = {col: selected_funcs for col in agg_cols}
                    
                    # Perform groupby operation
                    grouped_df = df.groupby(group_col).agg(agg_dict)
                    
                    # Display results
                    st.dataframe(grouped_df, use_container_width=True)
                    
                    # Visualize results
                    st.subheader("Visualization")
                    
                    # Flatten multi-index columns
                    grouped_df.columns = ['_'.join(col).strip() for col in grouped_df.columns.values]
                    grouped_df = grouped_df.reset_index()
                    
                    # Select column to visualize
                    viz_col = st.selectbox("Select column to visualize:", grouped_df.columns[1:])
                    
                    # Create bar chart
                    fig = px.bar(
                        grouped_df,
                        x=group_col,
                        y=viz_col,
                        title=f"{viz_col} by {group_col}",
                        text_auto='.2s'
                    )
                    st.plotly_chart(fig, use_container_width=True)

# Export page
elif selected == "Export":
    st.title("💾 Export Data")
    
    if not st.session_state.processed_dfs:
        st.warning("⚠️ Please upload or load sample data first!")
    else:
        # File selector
        file_names = list(st.session_state.processed_dfs.keys())
        selected_file = st.selectbox("Select a file to export:", file_names)
        df = st.session_state.processed_dfs[selected_file]
        
        # Export options
        st.subheader("Export Options")
        
        export_format = st.radio(
            "Select export format:",
            ["CSV", "Excel", "JSON", "HTML", "SQL", "Parquet", "Pickle"]
        )
        
        # Export options based on format
        if export_format == "CSV":
            delimiter = st.selectbox("Select delimiter:", [",", ";", "\t", "|"])
            include_index = st.checkbox("Include index", value=False)
            
            if st.button("Export to CSV"):
                csv_data = df.to_csv(sep=delimiter, index=include_index)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"{selected_file.split('.')[0]}_processed.csv",
                    mime="text/csv"
                )
        
        elif export_format == "Excel":
            include_index = st.checkbox("Include index", value=False)
            sheet_name = st.text_input("Sheet name:", "Sheet1")
            
            if st.button("Export to Excel"):
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=include_index)
                
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=buffer,
                    file_name=f"{selected_file.split('.')[0]}_processed.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        elif export_format == "JSON":
            orient_options = ["records", "split", "index", "columns", "values"]
            orient = st.selectbox("JSON orientation:", orient_options, index=0)
            
            if st.button("Export to JSON"):
                json_data = df.to_json(orient=orient)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_data,
                    file_name=f"{selected_file.split('.')[0]}_processed.json",
                    mime="application/json"
                )
        
        elif export_format == "HTML":
            include_index = st.checkbox("Include index", value=False)
            table_id = st.text_input("Table ID:", "dataframe")
            
            if st.button("Export to HTML"):
                html_data = df.to_html(index=include_index, table_id=table_id, classes="table table-striped table-hover")
                
                # Add some basic styling
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Data Sweeper Export</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        body {{ padding: 20px; }}
                        h1 {{ margin-bottom: 20px; }}
                        .table {{ width: 100%; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Data Export: {selected_file}</h1>
                        <p>Exported on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                        {html_data}
                    </div>
                </body>
                </html>
                """
                
                st.download_button(
                    label="⬇️ Download HTML",
                    data=styled_html,
                    file_name=f"{selected_file.split('.')[0]}_processed.html",
                    mime="text/html"
                )
        
        elif export_format == "SQL":
            table_name = st.text_input("Table name:", f"{selected_file.split('.')[0]}_table")
            sql_dialect = st.selectbox("SQL dialect:", ["sqlite", "mysql", "postgresql"])
            
            if st.button("Generate SQL"):
                # Generate CREATE TABLE statement
                create_table = f"CREATE TABLE {table_name} (\n"
                
                # Map pandas dtypes to SQL types
                dtype_map = {
                    'int64': 'INTEGER',
                    'float64': 'FLOAT',
                    'bool': 'BOOLEAN',
                    'datetime64[ns]': 'TIMESTAMP',
                    'object': 'TEXT'
                }
                
                # Add columns
                for col, dtype in df.dtypes.items():
                    sql_type = dtype_map.get(str(dtype), 'TEXT')
                    create_table += f"    {col} {sql_type},\n"
                
                # Remove trailing comma and close statement
                create_table = create_table.rstrip(',\n') + "\n);"
                
                # Generate INSERT statements (limited to first 10 rows for preview)
                insert_statements = []
                for i, row in df.head(10).iterrows():
                    values = []
                    for val in row:
                        if pd.isna(val):
                            values.append("NULL")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            values.append(f"'{str(val).replace('\'', '\'\'')}'")
                    
                    insert_statements.append(f"INSERT INTO {table_name} VALUES ({', '.join(values)});")
                
                # Combine statements
                sql_script = create_table + "\n\n" + "\n".join(insert_statements)
                
                # Display preview
                st.code(sql_script, language="sql")
                
                # Download button
                st.download_button(
                    label="⬇️ Download SQL Script",
                    data=sql_script,
                    file_name=f"{selected_file.split('.')[0]}_processed.sql",
                    mime="text/plain"
                )
        
        elif export_format == "Parquet":
            compression = st.selectbox("Compression:", ["snappy", "gzip", "brotli", "none"])
            
            if st.button("Export to Parquet"):
                buffer ="none"

            if st.button("Export to Parquet"):
                buffer = BytesIO()
                df.to_parquet(buffer, compression=None if compression == "none" else compression)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download Parquet",
                    data=buffer,
                    file_name=f"{selected_file.split('.')[0]}_processed.parquet",
                    mime="application/octet-stream"
                )

        elif export_format == "Pickle":
            protocol = st.slider("Pickle protocol version:", min_value=2, max_value=5, value=4)
            compression = st.selectbox("Compression:", ["None", "gzip", "bz2", "xz"])

            if st.button("Export to Pickle"):
                buffer = BytesIO()
                df.to_pickle(buffer, protocol=protocol, compression=None if compression == "None" else compression)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download Pickle",
                    data=buffer,
                    file_name=f"{selected_file.split('.')[0]}_processed.pkl",
                    mime="application/octet-stream"
                )

        # Export selected rows/columns
        st.subheader("Export Subset of Data")

        export_option = st.radio("Export:", ["All Data", "Selected Columns", "Filtered Data"])

        if export_option == "Selected Columns":
            selected_columns = st.multiselect("Select columns to export:", df.columns)

            if selected_columns:
                subset_df = df[selected_columns]
                st.dataframe(subset_df.head(), use_container_width=True)

                if st.button("Export Subset"):
                    csv_data = subset_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Subset CSV",
                        data=csv_data,
                        file_name=f"{selected_file.split('.')[0]}_subset.csv",
                        mime="text/csv"
                    )

        elif export_option == "Filtered Data":
            filter_column = st.selectbox("Select column to filter by:", df.columns)
            filter_type = st.selectbox("Filter type:", ["Contains", "Equals", "Greater than", "Less than", "Between"])

            if filter_type == "Contains":
                filter_value = st.text_input("Enter value to filter by:")
                if filter_value:
                    filtered_df = df[df[filter_column].astype(str).str.contains(filter_value, case=False)]

            elif filter_type == "Equals":
                filter_value = st.text_input("Enter value to filter by:")
                if filter_value:
                    filtered_df = df[df[filter_column].astype(str) == filter_value]

            elif filter_type == "Greater than":
                if df[filter_column].dtype.kind in 'ifc':
                    filter_value = st.number_input("Enter value:")
                    filtered_df = df[df[filter_column] > filter_value]
                else:
                    st.warning("⚠️ This filter type is only applicable to numeric columns.")
                    filtered_df = df

            elif filter_type == "Less than":
                if df[filter_column].dtype.kind in 'ifc':
                    filter_value = st.number_input("Enter value:")
                    filtered_df = df[df[filter_column] < filter_value]
                else:
                    st.warning("⚠️ This filter type is only applicable to numeric columns.")
                    filtered_df = df

            elif filter_type == "Between":
                if df[filter_column].dtype.kind in 'ifc':
                    col1, col2 = st.columns(2)
                    with col1:
                        min_value = st.number_input("Minimum value:")
                    with col2:
                        max_value = st.number_input("Maximum value:")
                    filtered_df = df[(df[filter_column] >= min_value) & (df[filter_column] <= max_value)]
                else:
                    st.warning("⚠️ This filter type is only applicable to numeric columns.")
                    filtered_df = df

            else:
                filtered_df = df

            st.write(f"Filtered data: {len(filtered_df)} rows")
            st.dataframe(filtered_df.head(), use_container_width=True)

            if len(filtered_df) > 0 and st.button("Export Filtered Data"):
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Filtered CSV",
                    data=csv_data,
                    file_name=f"{selected_file.split('.')[0]}_filtered.csv",
                    mime="text/csv"
                )

# Help page
elif selected == "Help":
    st.title("❓ Help & Documentation")

    st.markdown("""
    <div style='background-color: rgba(0, 120, 215, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3>Welcome to Data Sweeper Pro Help!</h3>
        <p>This guide will help you make the most of the Data Sweeper Pro application.</p>
    </div>
    """, unsafe_allow_html=True)

    help_tabs = st.tabs(["Getting Started", "Data Cleaning", "Visualization", "Analysis", "Export", "FAQ"])

    with help_tabs[0]:
        st.subheader("Getting Started")
        st.markdown("""
        ### Uploading Data

        1. Navigate to the **Home** page
        2. Use the file uploader to upload CSV, Excel, or JSON files
        3. You can upload multiple files at once
        4. Alternatively, you can use the sample data provided

        ### Navigation

        Use the sidebar menu to navigate between different sections:

        - **Home**: Upload and preview data
        - **Data Cleaning**: Clean and transform your data
        - **Visualization**: Create charts and visualizations
        - **Analysis**: Perform statistical analysis
        - **Export**: Export your processed data
        - **Help**: Get help and documentation

        ### Theme

        You can switch between Dark and Light themes using the theme selector in the sidebar.
        """)

    with help_tabs[1]:
        st.subheader("Data Cleaning")
        st.markdown("""
        The Data Cleaning section provides tools to clean and transform your data:

        ### Basic Cleaning
        - Remove duplicates
        - Remove empty rows
        - Remove or rename columns

        ### Missing Values
        - View missing value statistics
        - Fill missing values using various methods (mean, median, mode, etc.)
        - Drop rows with missing values

        ### Outliers
        - Detect outliers using box plots and IQR
        - Remove, cap, or replace outliers

        ### Data Types
        - View and change data types
        - Convert columns to int, float, string, datetime, etc.

        ### Custom Operations
        - Create new columns using expressions
        - Apply transformations to columns (uppercase, lowercase, rounding, etc.)
        """)

    with help_tabs[2]:
        st.subheader("Visualization")
        st.markdown("""
        The Visualization section allows you to create various charts and plots:

        ### Basic Charts
        - Bar charts
        - Line charts
        - Scatter plots
        - Pie charts
        - Histograms
        - Box plots

        ### Statistical Plots
        - Correlation heatmaps
        - Pair plots
        - Distribution plots
        - Violin plots

        ### Interactive Plots
        - 3D scatter plots
        - Bubble charts
        - Time series
        - Animated charts

        ### Custom Visualization
        - Create custom plots with specific parameters
        - Download plots as HTML files
        """)

    with help_tabs[3]:
        st.subheader("Analysis")
        st.markdown("""
        The Analysis section provides tools for statistical analysis:

        ### Summary Statistics
        - View basic statistics (mean, median, std dev, etc.)
        - View column-specific statistics

        ### Data Profiling
        - Generate comprehensive data profile reports

        ### Correlation Analysis
        - Calculate correlations between numeric columns
        - View correlation heatmaps
        - Identify top correlations

        ### Group Analysis
        - Group data by categorical columns
        - Calculate aggregations (mean, sum, count, etc.)
        - Visualize group analysis results
        """)

    with help_tabs[4]:
        st.subheader("Export")
        st.markdown("""
        The Export section allows you to export your processed data:

        ### Export Formats
        - CSV
        - Excel
        - JSON
        - HTML
        - SQL
        - Parquet
        - Pickle

        ### Export Options
        - Export all data
        - Export selected columns
        - Export filtered data

        ### Format-specific Options
        - CSV: delimiter, include index
        - Excel: sheet name, include index
        - JSON: orientation
        - HTML: styling, table ID
        - SQL: table name, dialect
        - Parquet: compression
        - Pickle: protocol, compression
        """)

    with help_tabs[5]:
        st.subheader("Frequently Asked Questions")
        st.markdown("""
        ### What file formats are supported?
        Data Sweeper Pro supports CSV, Excel (xlsx, xls), and JSON files.

        ### Is there a limit to file size?
        Streamlit has a default file size limit of 200MB. Large files may cause performance issues.

        ### Can I save my work?
        Currently, the app doesn't support saving sessions. You should export your processed data before closing the app.

        ### How do I report bugs or request features?
        Please contact the developer with any issues or feature requests.

        ### Is my data secure?
        Your data is processed locally in your browser and is not stored on any server.

        ### Can I use this app offline?
        Yes, you can run this app locally by installing Streamlit and the required dependencies.
        """)

    # Contact information
    st.subheader("Contact")
    st.markdown("""
    If you have any questions, feedback, or need assistance, please contact us:

    - **Email**: support@datasweeper.example.com
    - **GitHub**: [github.com/datasweeper](https://github.com/datasweeper)
    """)

