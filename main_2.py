
from py5paisa import *
from datetime import *
import pytz
import time
import pandas as pd
import pyotp
from deta import Deta

nf_lot=550
bnf_lot=250



def get_BookedPL(client):
    BookedPL=0
    for pos in client.positions():
        BookedPL+=pos['BookedPL']
        BookedPL+=pos['MTOM']
    return BookedPL

key='d0p3jsxc_jAhdkSrj194KPkx9YX8iDRZzZCBKQPfP'

def insert_val(BookedPL,bnf,nf):
    deta = Deta(key)
    users = deta.Base("option_sell_db")
    users.insert({"DateTime": str(datetime.now(pytz.timezone('Asia/Kolkata'))).split('.')[0], "Profit": str(BookedPL),"BNF": str(bnf),"NF": str(nf)})

def get_switch():
    # return 'ON'
    deta = Deta(key)
    users = deta.Base("switch")
    fetch_res = users.fetch({"key": "ua1hy6g6qak6"})
    return fetch_res.items[0]['Switch']


def check_market_timing():
    if datetime.now(pytz.timezone('Asia/Kolkata')).hour == 9:
        if datetime.now(pytz.timezone('Asia/Kolkata')).minute >= 20  and get_switch()=='ON':
            return True
    elif datetime.now(pytz.timezone('Asia/Kolkata')).hour > 9 and datetime.now(pytz.timezone('Asia/Kolkata')).hour < 16 and get_switch()=='ON':
        return True
    return False

def squareoff_all_positions(client):
    for pos in client.positions():
        NetQty=pos['NetQty']
        if NetQty>0:
            LTP=pos['LTP']-2
            ScripCode=int(pos['ScripCode'])
            client.place_order(OrderType='S', Exchange='N', ExchangeType='D', ScripCode=ScripCode, Qty=NetQty, Price=LTP)
            print('SquareOff '+pos['ScripName'])



from keep_alive_replit import keep_alive
keep_alive()


def closest_index(lst, K):
    return min(range(len(lst)), key=lambda i: abs(lst[i] - K))

def get_option_chain(client,asset):
    k=client.get_expiry("N",asset)
    latest_expiry=[]
    for i in k['Expiry']:
        latest_expiry.append(i['ExpiryDate'][6:19])
    # print(latest_expiry)
            
    k = client.get_option_chain("N", asset, latest_expiry[0])
    k = (k['Options'])
    df = pd.DataFrame(k)[['CPType','LastRate','StrikeRate','ScripCode']]
    ce_df=df[df.CPType=='CE']
    ce_df.reset_index(inplace=True,drop=True)
    pe_df=df[df.CPType=='PE']
    pe_df.reset_index(inplace=True,drop=True)

    return [ce_df,pe_df]


def broker_login():

    totp = pyotp.TOTP('GUYTIMJZGM3DCXZVKBDUWRKZ').now()
    cred = {
            "APP_NAME": "5P51419361",
            "APP_SOURCE": "11179",
            "USER_ID": "FKTvPb6GrxX",
            "PASSWORD": "Rf7SoLvxXcj",
            "USER_KEY": "LCHhAHfRrkeDwQkjHyGtQGFmBkl1h50T",
            "ENCRYPTION_KEY": "c5yN3Ny1k4zj272fI40YDzHrF4Q1dics"
        }


    client = FivePaisaClient(cred=cred)

    totp_str=str(totp)
    print(totp_str)
    client.get_totp_session('51419361',totp_str,'000000')

    return client




def option_hedge(client):

    time_now = datetime.now(pytz.timezone('Asia/Kolkata'))
    print('Time Now = ',time_now)
    to_ = time_now.date() + timedelta(days=2)
    from_ = time_now.date() - timedelta(days=2)

    # df_NF = client.historical_data('N', 'C', 999920043, '1m', str(from_),str(to_))
    # df_BNF = client.historical_data('N', 'C', 999920005, '1m', str(from_),str(to_))

    df_NF = client.historical_data('N', 'C', 1333, '1m', str(from_),str(to_))
    df_BNF = client.historical_data('N', 'C', 2885, '1m', str(from_),str(to_))

    df_NF['Date']=df_NF['Datetime'].apply(lambda x: x.split('T')[0])
    df_BNF['Date']=df_BNF['Datetime'].apply(lambda x: x.split('T')[0])

    ll=str(time_now).split(' ')[0]

    
    df_NF=df_NF[df_NF.Date==str(time_now).split(' ')[0]]
    df_BNF=df_BNF[df_BNF.Date==str(time_now).split(' ')[0]]
    

    

    bnf=list(df_BNF.loc[df_BNF['Date']==ll,'Close'])[1:]
    nf=list(df_NF.loc[df_NF['Date']==ll,'Close'])[1:]

    df_date=list(df_NF['Date'])
    
    st_bnf=bnf[0]
    st_nf=nf[0]
    
    ls_bnf=[x/st_bnf for x in bnf]
    ls_nf=[x/st_nf for x in nf]
    
    # df_SMA_Flag=get_profit_sma(ls_bnf,ls_nf,bnf,nf)
    # print(df_SMA_Flag)
    # df_SMA_Flag=df_SMA_Flag.Is_True.to_list()[-2]
    # print('=================')
    # print('SMA Flag')
    # print(df_SMA_Flag)
    # print('=================')

    BookedPL=get_BookedPL(client)

    df_SMA_Flag=True
    if BookedPL>2000:
        df_SMA_Flag=False

    flag=''

    # if (ls_bnf[-2]>ls_nf[-2]) and (ls_bnf[-3]<ls_nf[-3]):
    #     flag='BNF'
    # if (ls_bnf[-2]<ls_nf[-2]) and (ls_bnf[-3]>ls_nf[-3]):
    #     flag='NF'

    if (ls_bnf[-2]>ls_nf[-2]):
        flag='BNF'
    if (ls_bnf[-2]<ls_nf[-2]):
        flag='NF'


    print(ls_bnf[-5:])
    print(ls_nf[-5:])


    print('flag = ',flag)
    
    
    BNF_Close=df_BNF.Close.values[-1]
    NF_Close=df_NF.Close.values[-1]


    print('BankNifty = ',BNF_Close)
    print('Nifty = ',NF_Close)

    # df_option=get_option_chain(client,'BANKNIFTY')
    df_option=get_option_chain(client,'RELIANCE')

    ce_df=df_option[0]
    pe_df=df_option[1]

    print('BankNifty ++++ Option')

    # print("CE = ",ce_df.loc[closest_index(list(ce_df.StrikeRate), BNF_Close-10)].StrikeRate)
    # print("PE = ",pe_df.loc[closest_index(list(pe_df.StrikeRate), BNF_Close+10)].StrikeRate)



    # BNF_ce_ScripCode = ce_df.loc[closest_index(list(ce_df.StrikeRate), BNF_Close-10)].ScripCode
    # BNF_pe_ScripCode = pe_df.loc[closest_index(list(pe_df.StrikeRate), BNF_Close+10)].ScripCode

    print("CE = ",ce_df.loc[closest_index(list(ce_df.StrikeRate), BNF_Close)].StrikeRate)
    print("PE = ",pe_df.loc[closest_index(list(pe_df.StrikeRate), BNF_Close)].StrikeRate)



    BNF_ce_ScripCode = ce_df.loc[closest_index(list(ce_df.StrikeRate), BNF_Close)].ScripCode
    BNF_pe_ScripCode = pe_df.loc[closest_index(list(pe_df.StrikeRate), BNF_Close)].ScripCode



    # df_option=get_option_chain(client,'Midcpnifty')
    df_option=get_option_chain(client,'HDFCBANK')

    ce_df=df_option[0]
    pe_df=df_option[1]

    print('Nifty ++++ Option')

    # print("CE = ",ce_df.loc[closest_index(list(ce_df.StrikeRate), NF_Close-20)].StrikeRate)
    # print("PE = ",pe_df.loc[closest_index(list(pe_df.StrikeRate), NF_Close+20)].StrikeRate)



    # NF_ce_ScripCode = ce_df.loc[closest_index(list(ce_df.StrikeRate), NF_Close-20)].ScripCode
    # NF_pe_ScripCode = pe_df.loc[closest_index(list(pe_df.StrikeRate), NF_Close+20)].ScripCode


    print("CE = ",ce_df.loc[closest_index(list(ce_df.StrikeRate), NF_Close)].StrikeRate)
    print("PE = ",pe_df.loc[closest_index(list(pe_df.StrikeRate), NF_Close)].StrikeRate)



    NF_ce_ScripCode = ce_df.loc[closest_index(list(ce_df.StrikeRate), NF_Close)].ScripCode
    NF_pe_ScripCode = pe_df.loc[closest_index(list(pe_df.StrikeRate), NF_Close)].ScripCode

    proceed_flag=True
    if datetime.now(pytz.timezone('Asia/Kolkata')).hour == 15 and datetime.now(pytz.timezone('Asia/Kolkata')).minute >=20:
        # client.squareoff_all()
        squareoff_all_positions(client)
        proceed_flag=False
    
    if df_SMA_Flag==False:
        squareoff_all_positions(client)
        proceed_flag=False


    open_flag=''
    for pos in client.positions():
        # print(pos)
        if 'RELIANCE' in pos['ScripName'] and 'CE'in pos['ScripName'] and pos['NetQty']>0:
            open_flag='BNF'
            break
        elif 'HDFCBANK' in pos['ScripName'] and 'CE'in pos['ScripName'] and pos['NetQty']>0:
            open_flag='NF'
            break
        else:
            open_flag='No_Open_Positions'
    
            
    
    print('open_flag = ',open_flag)

    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": str(NF_pe_ScripCode)}]

    ltp_pe_option_price=(client.fetch_market_feed_scrip(req_list_)['Data'][0]['LastRate'])+2

    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": str(NF_ce_ScripCode)}]

    ltp_ce_option_price=(client.fetch_market_feed_scrip(req_list_)['Data'][0]['LastRate'])+2

    print(ltp_pe_option_price,ltp_ce_option_price)



    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": str(BNF_pe_ScripCode)}]

    B_ltp_pe_option_price=(client.fetch_market_feed_scrip(req_list_)['Data'][0]['LastRate'])+2

    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": str(BNF_ce_ScripCode)}]

    B_ltp_ce_option_price=(client.fetch_market_feed_scrip(req_list_)['Data'][0]['LastRate'])+2

    print(B_ltp_pe_option_price,B_ltp_ce_option_price)



            
    if flag=='BNF' and open_flag !='BNF' and proceed_flag and df_SMA_Flag:
        open_flag='BNF'
        # client.squareoff_all()
        squareoff_all_positions(client)
        client.place_order(OrderType='B', Exchange='N', ExchangeType='D', ScripCode=int(BNF_ce_ScripCode), Qty=bnf_lot, Price=B_ltp_ce_option_price)
        client.place_order(OrderType='B', Exchange='N', ExchangeType='D', ScripCode=int(NF_pe_ScripCode), Qty=nf_lot, Price=ltp_pe_option_price)
        print('BNF Long')

    if flag=='NF' and open_flag!='NF' and proceed_flag and df_SMA_Flag:
        open_flag='NF'
        # client.squareoff_all()
        squareoff_all_positions(client)
        client.place_order(OrderType='B', Exchange='N', ExchangeType='D', ScripCode=int(NF_ce_ScripCode), Qty=nf_lot, Price=ltp_ce_option_price)
        client.place_order(OrderType='B', Exchange='N', ExchangeType='D', ScripCode=int(BNF_pe_ScripCode), Qty=bnf_lot, Price=B_ltp_pe_option_price)
        print('NF Long')


    BookedPL=get_BookedPL(client)
    insert_val(BookedPL,BNF_Close,NF_Close)



if __name__ == '__main__':
  while True:
    day_number=datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
    print('Loop Time ', datetime.now(pytz.timezone('Asia/Kolkata')))
    time.sleep(10)
    if check_market_timing() and (day_number not in [5,6]) and get_switch()=='ON':
      broker = broker_login()
      while True:
        print('Running ', datetime.now(pytz.timezone('Asia/Kolkata')))
        time.sleep(10)
        print(check_market_timing() and get_switch()=='ON')
        print(get_switch()=='ON')
        if check_market_timing() and get_switch()=='ON':
            option_hedge(broker)
        else:
          break
