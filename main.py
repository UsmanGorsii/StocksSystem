from flask import Flask, render_template, flash, request, url_for, jsonify, redirect, session
from modules.DBController import DBController
from modules.UserController import UserController
from modules.ScrapeRecords import StocksScraper
from flask_apscheduler import APScheduler
from datetime import datetime
app = Flask(__name__)
app.secret_key = "2e1dt3476rtfghudigyugqwwu2w8190qoidj"
db = UserController('users.sql')
db.show_records()
username = db.get_record()[0]
password = db.get_record()[1]
db.close_connection()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scraping_status = ""

@app.route('/', methods=['GET', 'POST'])
@app.route('/inputPage', methods=['GET', 'POST'])
def input_page():
    if not session.get('logged_in'):
        return render_template('pages-login.html', title='Login Page')

    return render_template('inputPage.html', title="Home Page", scraping_status=scraping_status)


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.method == "POST" and request.form['password'] == password and request.form['username'] == username:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return input_page()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return input_page()


# rendering HTML Page to Show all data in table form
@app.route('/tableDetails', methods=['GET', 'POST'])
def table_details():
    if not session.get('logged_in'):
        return render_template('pages-login.html', title='Login Page')
    db = DBController("StocksDb.sql")
    if request.method == "POST":
        all_filtered_rows = db.get_filtered_records(request.form['minPercentage'],
                                                    request.form['maxPercentage'],
                                                    datetime.strptime(request.form['date'],
                                                                      '%Y-%m-%d').strftime
                                                                     ('%m-%d-%Y'))
    else:
        all_filtered_rows = db.get_today_records()
    db.close_connection()

    return render_template('tableDetails.html', title='Table Details Page', tableData=all_filtered_rows)


@app.route('/startScraping')
def initiate_scraping():
    global scraping_status
    if scraping_status != "Scraping in Progress...":
        scraping_status = "Scraping in Progress..."
        app.apscheduler.add_job(func=start_scraping, trigger='date', args=[], id='j' + str(1))

    return input_page()


def start_scraping():
    global scraping_status
    scraper = StocksScraper()
    scraper.start_scraping()
    scraping_status = "Finished Scraping"

@app.route('/tableChanges', methods=['GET', 'POST'])
def table_changes():
    if not session.get('logged_in'):
        return render_template('pages-login.html', title='Login Page')
    else:
        columns = ["stock_id"]
        db = DBController("StocksDb.sql")
        result = db.get_last_few_dates()

        row = {}
        for item in list(set(result)):
            row[item] = {"status": "", "change": ""}
            columns.append(item)

        data = db.get_last_few_days()
        data_dict = {}
        for d in data:
            if d[0] not in (data_dict.keys()):
                import copy
                data_dict[d[0]] = copy.deepcopy(row)
            data_dict[d[0]][d[1]]['status'] = d[2]
            data_dict[d[0]][d[1]]['change'] = d[6]
        print(data_dict)
        return render_template("tableChanges.html", title="Table Changes Page",
                               columnsData=columns, tableData=data_dict)


if __name__ == '__main__':
    app.run(debug=True)
