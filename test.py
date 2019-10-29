from bs4 import BeautifulSoup

with open("hm.html", "r", encoding="utf-8") as inputf:
    soup = BeautifulSoup(inputf.read(), "html.parser")
with open("all_companies.txt", "w") as output:
    for code_soup in soup.find_all('td', {"class": "code"}):
        output.writelines(code_soup.text.strip() + "\n")