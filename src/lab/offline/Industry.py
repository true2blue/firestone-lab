import akshare as ak

stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
stock_board_industry_name_em_df.to_csv('./output/industry.csv', index=False)