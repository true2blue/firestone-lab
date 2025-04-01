import akshare as ak

# stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
# print(stock_board_concept_name_em_df)
# stock_board_concept_name_em_df.to_csv('./output/stock_board_concept_name_em_df.csv', index=False)


stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol='AI制药（医疗）')
print(stock_board_concept_cons_em_df)
stock_board_concept_cons_em_df.to_csv('./output/stock_board_concept_cons_em_df.csv', index=False)