import akshare as ak

stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
stock_board_concept_name_em_df.to_csv('./output/concepts.csv', index=False)