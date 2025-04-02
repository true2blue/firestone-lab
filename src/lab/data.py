import pandas as pd

# Load the data from the CSV file
file_path = 'data/raw/002084-2025-04-02.csv'
code = '002084'
name = '海鸥住工'
pre_close = 2.85
data = pd.read_csv(file_path)

# Ensure numeric columns are properly converted
numeric_columns = ['成交','金额','笔数']
for col in numeric_columns:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

# Drop rows with NaN in numeric columns
data = data.dropna(subset=numeric_columns)

# Display the first few rows of the data
data['时间'] = data['时间'].apply(lambda x: f"0{x}" if len(x) == 4 and x[1] == ':' else x)
data['秒'] = data.groupby('时间').cumcount() * 3
data['秒'] = data['秒'].apply(lambda x: f":0{x}" if x < 10 else f":{x}")
data['时间'] = data['时间'] + data['秒']
data = data[data['时间'] >= '09:25:00']
data.rename(columns={'成交': '最新价'}, inplace=True)
data['成交额'] = data['金额'].cumsum()
data['代码'] = code
data['名称'] = name
data['昨收'] = pre_close
data['今开'] = data.loc[data['时间'] == '09:25:00', '最新价'].iloc[-1] if not data.loc[data['时间'] == '09:25:00'].empty else None
data['最高'] = data['最新价'].cummax()
data['最低'] = data['最新价'].cummin()
data['涨跌幅'] = ((data['最新价'] - pre_close) / pre_close * 100).round(2)
data['振幅'] = ((data['最高'] - data['最低']) / pre_close * 100).round(2)
# Optionally, you can use latest_price_at_0925 for further processing if needed
# Save the modified data to a new CSV file
output_file_path = 'data/processed/002084-2025-04-02.csv'
data.to_csv(output_file_path, index=False)