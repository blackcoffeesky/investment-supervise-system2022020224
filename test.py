from gm.api import *

token = "bda305b573432b1d8a918855d1b439c3d09671aa"
account = "2ac43580-715f-4cc5-93d7-83fccc7b7997"
set_token(token)

# set_account_id("1fd2189a-09ec-11f0-9063-00163e022aa6")


if __name__ == '__main__':
    print(get_cash(account)['available'])
    position = get_position(account)
    for i in position:
        print(i['symbol'], i['volume'],i['vwap'],i['price'])
    print(position[0])
    print(get_orders())