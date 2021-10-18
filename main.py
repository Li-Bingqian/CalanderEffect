# This is a script that researches on Calendar Effect.
import matplotlib.pyplot as plt

from ps_tool_kit import pd, np
from ps_tool_kit.connect_to_database import connect_sqlite
from ps_tool_kit.date_N_time import gen_trade_date
import json
import matplotlib.pyplot as plt


def get_trades(x):
    """
    sum trades number for dictionaries in each square
    :param x: list of dictionaries
    :return: sum trades number
    """
    trades = sum(json.loads(json.dumps(eval(x))).values())
    return trades


def get_trades_number(day_list):
    """
    get data from db and sum total trade number for each record
    read columns: buymtrades, sellmtrades (list of dictionaries, add all values)
    :param day_list: data of those dates
    :return: datframe including timestamp and trades number
    """
    # Use a breakpoint in the code line below to debug your script.
    path = 'C:/Users/Aubree/OneDrive - KuCoin/文档 - 铂石量化分析组/DataBase/all_trades_km/Trades_KCM_XBTUSDTM.db'
    cursor_contract = connect_sqlite(path)
    list_of_dataframes = []

    for table_name in day_list:
        cursor_contract.execute("SELECT datetime, buymtrades, sellmtrades  FROM '%s'" % table_name)
        con_df = pd.DataFrame(cursor_contract.fetchall(),
                              columns=(['datetime', "buy_m", "sell_m"])).set_index('datetime')
        list_of_dataframes.append(con_df)
    con_df = pd.concat(list_of_dataframes)
    buy_df = con_df["buy_m"]
    sell_df = con_df["sell_m"]
    buy_trades = buy_df.apply(get_trades)
    sell_trades = sell_df.apply(get_trades)
    result = pd.DataFrame({"buy_trades": buy_trades, "sell_trades":sell_trades})
    return result


def plot_trades_freq(trade_num_df, date, side, win_len):
    """
    plot daily trades number by certain window length
    :param trade_num_df: the date frame contains trades number every 100ms
    :param date: the date to plot
    :param side: the side to plot, buy or sell
    :param win_len: group by this frequency
    :return:
    """
    df_date = trade_num_df[trade_num_df.date == date].copy()
    df_date["all_trades"] = df_date.buy_trades + df_date.sell_trades
    df_date['window'] = [x.time() for x in df_date.index.floor(str(win_len) + 'S')]
    df_date = df_date.groupby("window").sum()
    time = df_date.index.map(lambda t: str(t))      # x axis

    fig, ax = plt.subplots()
    # Make a bar plot, ignoring the date values
    ax.bar(time, df_date[side + "_trades"], align='center', width=0.5)
    plt.xticks(np.arange(0, (len(time)), 1),
               [time[i][:2] if i in range(0, len(time), 4) else '' for i in range( len(time))],
               rotation=45, size=9)     # deal with x axis overlapping
    # plt.bar(x=dt, height=df_date.buy_trades)
    # plt.xticks()
    plt.xlabel("Hour")
    plt.ylabel("Trade Number")
    plt.title("%s %s trades in %d seconds" % (str(date), side, win_len))
    plt.savefig("./plot_result/%s_%s_%d.png" % (side, str(date), win_len))


def excel_show(day_list, side):
    from openpyxl import load_workbook
    from openpyxl.drawing.image import Image
    excel_address = r"C:\Users\Aubree\OneDrive - KuCoin\桌面\work\CalanderEffect\plot_result_" + side +".xlsx"
    wb = load_workbook(excel_address)
    sht = wb.worksheets[0]

    # dates = ['2021-07-' + str(d) for d in range(21, 28)]
    i = 1
    for d in day_list:
        img_address_1 = r"C:\Users\Aubree\OneDrive - KuCoin\桌面\work\CalanderEffect\plot_result\%s_%s_%d.png" % (side, str(d), 900)
        img = Image(img_address_1)
        sht.add_image(img, 'A%d' % i)
        sht.column_dimensions['A'].width = 100.0
        sht.row_dimensions[i].height = 400.0
        img_address_1 = r"C:\Users\Aubree\OneDrive - KuCoin\桌面\work\CalanderEffect\plot_result\%s_%s_%d.png" % (side, str(d), 1800)
        img = Image(img_address_1)
        sht.add_image(img, 'B%d' % i)
        sht.column_dimensions['B'].width = 100.0
        sht.row_dimensions[i].height = 400.0
        img_address_1 = r"C:\Users\Aubree\OneDrive - KuCoin\桌面\work\CalanderEffect\plot_result\%s_%s_%d.png" % (side, str(d), 3600)
        img = Image(img_address_1)
        sht.add_image(img, 'C%d' % i)
        sht.column_dimensions['C'].width = 100.0
        sht.row_dimensions[i].height = 400.0
        img_address_1 = r"C:\Users\Aubree\OneDrive - KuCoin\桌面\work\CalanderEffect\plot_result\%s_%s_%d.png" % (side, str(d), 7200)
        img = Image(img_address_1)
        sht.add_image(img, 'D%d' % i)
        sht.column_dimensions['D'].width = 100.0
        sht.row_dimensions[i].height = 400.0
        i += 1
    wb.save(excel_address)


def top_tades_time(trade_num_df, date, side, win_len, top_n):
    """
    plot daily trades number by certain window length
    :param top_n: n top displayed (1:3)
    :param trade_num_df: the date frame contains trades number every 100ms
    :param date: the date to plot
    :param side: the side to plot, buy or sell
    :param win_len: group by this frequency
    :return:
    """
    df_date = trade_num_df[trade_num_df.date == date].copy()
    df_date["all_trades"] = df_date.buy_trades + df_date.sell_trades
    df_date['window'] = [x.time() for x in df_date.index.floor(str(win_len) + 'S')]
    df_date = df_date.groupby("window").sum().loc[:, side+"_trades"]
    df_top = df_date.sort_values().iloc[:top_n]
    df_re = pd.DataFrame(df_top.index.to_list(),
                         index=["top" + str(x+1) for x in range(top_n)],
                         columns=[str(date)]).T
    df_re["window_length"] = win_len
    df_re["side"] = side
    df_re["top1_trades_num"] = df_top.iloc[0]
    return df_re


if __name__ == '__main__':
    # How to get trade numbers

    # trade_num = get_trades_number(day_ls)
    # trade_num.index = pd.to_datetime(trade_num.index.tolist(), format='%Y-%m-%d %H:%M:%S')
    # trade_num["date"] = trade_num.index.date
    # trade_num.to_csv("./trade_num_all.csv")
    start_date = "2021-07-21"
    end_date = "2021-07-27"
    a_day_ls = gen_trade_date(start_date, end_date)
    b_day_ls = ["2021-08-" + str(i) for i in list(range(19, 26, 1))] + \
             ["2021-09-07", "2021-09-12", "2021-09-21", "2021-09-28", "2021-09-29", "2021-10-01", "2021-10-07"]
    day_ls = a_day_ls + b_day_ls
    trade_num = pd.read_csv("./trade_num_all.csv", index_col=0)
    trade_num.index = pd.to_datetime(trade_num.index.tolist(), format='%Y-%m-%d %H:%M:%S.%f')

    for day in day_ls:
        for i in [900, 1800, 3600, 7200]:
            for s in ["buy", "sell", "all"]:
                print(day, i, s)
                plot_trades_freq(trade_num, day, s, i)
    for s in ["buy", "sell", "all"]:
        ls_result = []
        for day in day_ls:
            for i in [900, 1800, 3600, 7200]:
                df_temp = top_tades_time(trade_num, day, s, i, 3)
                ls_result.append(df_temp)
        df_result = pd.concat(ls_result)
        df_result.to_csv("./top3_times_%s.csv" % s)

    # date = trade_num.date.unique()[0]
    # win_len = 900
    # side = "buy"
    # excel_show(day_ls, "buy")
