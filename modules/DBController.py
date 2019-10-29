import sqlite3
from datetime import datetime, timedelta


class DBController:
    def __init__(self, data_base):
        self.conn = sqlite3.connect(data_base)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS stocks"
                         "(Code text, Date date, Status text, CurrentPrice real, LowestPrice real,"
                         "HighestPrice real, ChangePercentage real, PercentageToLowest real"
                         ", PercentageToHighest real)")
        self.conn.commit()

    def insert_record(self, records=None):
        self.cur.executemany("INSERT INTO stocks VALUES "
                             "(?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
        self.conn.commit()

    def show_records(self):
        for row in self.cur.execute('SELECT * FROM stocks'):
            print(row)

    def get_filtered_records(self, p_to_low, p_to_high, date_arg):
        all_rows = []
        for row in self.cur.execute('SELECT * FROM stocks '
                                    'where PercentageToLowest >= ? and PercentageToHighest >= ?'
                                    'and Date = ?', (p_to_low, p_to_high,
                                                     date_arg,)):
            all_rows.append(row)
        return all_rows

    def get_today_records(self):
        all_rows = []
        for row in self.cur.execute\
                    ('SELECT * FROM stocks '
                     'where '
                     'Date = ?', (datetime.now().strftime("%m-%d-%Y"),)):
            all_rows.append(row)
        return all_rows

    def get_last_few_dates(self):
        all_rows = []
        for row in self.cur.execute \
                    ('SELECT Date FROM stocks '
                     'where '
                     'Date >= ?', ((datetime.now() - timedelta(days=5)).strftime("%m-%d-%Y"),)):
            all_rows.append(row[0])
        return all_rows

    def get_last_few_days(self):
        all_rows = []
        for row in self.cur.execute \
                    ('SELECT * FROM stocks '
                     'where '
                     'Date >= ?', ((datetime.now() - timedelta(days=5)).strftime("%m-%d-%Y"),)):
            all_rows.append(row)
        return all_rows

    def close_connection(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    db = DBController("StocksDb.sql")
    result = db.get_last_few_dates()
    row = {"stock_id" : ""}
    for item in list(set(result)):
        row[item] = {"status": "", "change": ""}
    print(row)
    data = db.get_last_few_days()
    data_dict = {}
    for d in data:
        if d[0] not in (data_dict.keys()):
            import copy
            data_dict[d[0]] = copy.deepcopy(row)
        data_dict[d[0]]['stock_id'] = d[0]
        data_dict[d[0]][d[1]]['status'] = d[2]
        data_dict[d[0]][d[1]]['change'] = d[6]
    print(data_dict)

    db.close_connection()