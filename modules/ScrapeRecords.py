from modules.DBController import DBController
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup


class StocksScraper:
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "www.aastocks.com",
            "Referer": "http://www.aastocks.com/en/stocks/quote/symbolsearch.aspx?page=1&order=symbol&seq=asc",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }

        self.db = DBController("StocksDb.sql")
        self.set_all_companies()

    def set_all_companies(self):
        with open("all_companies.txt", "r") as companies_file:
            self.all_companies = companies_file.readlines()

    def start_scraping(self):
        s = requests.session()
        s.headers.update(self.headers)
        for i in self.all_companies:
            query = i.replace("\n", "").zfill(5)
            content_url = 'http://www.aastocks.com/en/stocks/quote/quick-quote.aspx?symbol={0}'.format(query)
            print(query)
            while True:
                try:
                    response = s.get(content_url)
                    break
                except:
                    pass
            try:
                open("output.html", "w", encoding="utf8").write(response.text)
                soup = BeautifulSoup(response.text, "html.parser")
                result = soup.find(lambda tag: tag.name == "font" and query == tag.text)
                if result is None:
                    table_soup = soup.find("table", {"class": "tblM"})
                    current_value = table_soup.find("td", class_="rel lastBox c1").text
                    current_value = current_value.split("-")[-1].strip().split(" ")[-1].strip()
                    if "▲" in current_value:
                        status = "increased"
                        current_value = current_value.replace('▲', "")
                    elif "▼" in current_value:
                        status = "decreased"
                        current_value = current_value.replace('▼', "")
                    else:
                        status = "no change"
                    change_percentage = table_soup.find("td", class_="chgBox rel").text
                    change_percentage = change_percentage.replace('Chg(%)', "").replace("%", "").strip()
                    if "▲" in change_percentage:
                        change_percentage = change_percentage.replace("▲", "")
                    elif "▼" in change_percentage:
                        change_percentage = change_percentage.replace("▼", "")
                    try:
                        week_dif_range = table_soup.find(lambda tag: tag.name == "td" and "52 WK" in tag.text).text.replace("52 WK", "").strip()
                        if "N/A" not in week_dif_range:
                            week_dif_min = week_dif_range.split("-")[0].strip()
                            week_dif_max = week_dif_range.split("-")[1].strip()
                    except:
                        week_dif_min = 0
                        week_dif_max = 0

                    try:
                        current_value = float(current_value)
                        change_percentage = float(change_percentage)
                        week_dif_min = float(week_dif_min)
                        week_dif_max = float(week_dif_max)
                        perToLow = (1 - (float(week_dif_min) / float(current_value))) * 100
                        perToHigh = (1 - (float(current_value) / float(week_dif_max))) * 100
                        self.db.insert_record([(query, datetime.now().strftime("%m-%d-%Y"), status, current_value, week_dif_min,
                                           week_dif_max, change_percentage, perToLow, perToHigh)])
                    except Exception as e:
                        print(e)
            except:
                pass
        s.close()