from sites.yuyutei import Yuyutei
from data.card import Card

playset = ['RR+', 'RR', 'R', 'U', 'C', 'CR', 'CC']
code = '5hy/w83'

data = Yuyutei(code)

report = data.get_report()

total_price, instock_price, missing = report.get_playset_price(*playset)

print(f'Set: {code.upper()}\n---------------------\nPlayset price: {total_price}\nInstock price: {instock_price}\n')
print('Missing\n---------------------')
for m in missing:
    print(f'{m[0]}: {m[1]}')