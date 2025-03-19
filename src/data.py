import pandas as pd

# Load the data from the CSV file
file_path = 'data/raw/600178-2025-03-19.csv'
code = '600178'
name = '东安动力'
pre_close = 12.10
data = pd.read_csv(file_path)

# Display the first few rows of the data
data['时间'] = data['时间'].apply(lambda x: f"0{x}" if len(x) == 4 and x[1] == ':' else x)
data.rename(columns={'成交': '最新价'}, inplace=True)
data['成交额'] = data['金额'].cumsum()
data['代码'] = code
data['名称'] = name
data['昨收'] = pre_close
data['今开'] = data.loc[data['时间'] == '09:25', '最新价'].iloc[-1] if not data.loc[data['时间'] == '09:25'].empty else None
data['最高'] = data['最新价'].cummax()
data['最低'] = data['最新价'].cummin()
data['涨跌幅'] = ((data['最新价'] - pre_close) / pre_close * 100).round(2)
data['振幅'] = ((data['最高'] - data['最低']) / pre_close * 100).round(2)
# Optionally, you can use latest_price_at_0925 for further processing if needed
# Save the modified data to a new CSV file
output_file_path = 'data/processed/600178-2025-03-19.csv'
data.to_csv(output_file_path, index=False)