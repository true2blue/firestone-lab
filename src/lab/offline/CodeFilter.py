import logging
import configparser
import akshare as ak
import pandas as pd

class CodeFilter(object):

    _logger = logging.getLogger(__name__)

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(f'./config/{config_file}', encoding='utf-8')
    
    
    def filter(self, concepts):
        result_df = pd.DataFrame()
        for symbol in concepts:
            stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol=symbol)
            stock_board_concept_cons_em_df['concept'] = symbol
            result_df = pd.concat([result_df, stock_board_concept_cons_em_df], ignore_index=True)
        result_df.drop_duplicates(subset=['代码'], inplace=True)
        result_df = result_df[~result_df['名称'].str.startswith(('ST', '*'))]
        result_df = result_df[~result_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
        result_df.to_csv('./output/codes.csv', index=False)


if __name__ == '__main__':
    CodeFilter().filter(['大飞机'])