import akshare as ak

stock_rank_ljqs_ths_df = ak.stock_rank_ljqs_ths()
stock_rank_ljqs_ths_df.to_csv('./output/indicator.csv', index=False)