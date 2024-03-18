import requests
from bs4 import BeautifulSoup

# 获取页面内容，返回BeautifulSoup对象
def get_html_content(url):
    while True:
        try:
            response = requests.get(url, timeout=1)
            response.encoding = "utf-8"
            if response.status_code == 200:
                return BeautifulSoup(response.text, "lxml")
            else:
                continue
        except Exception as e:
            print(f"Error fetching URL: {url}")
            print(e)
            continue

# 获取地址前缀
def get_url_prefix(url):
    return url[:url.rindex("/") + 1]

# 递归抓取下一页面的信息
def crawl_next_level(url, level, parent_code, file):
    level_names = {2: "city", 3: "county", 4: "town", 5: "village"}

    item_list = get_html_content(url).select(f"tr.{level_names[level]}tr")
    if item_list:
        for item in item_list:
            item_td = item.select("td")
            item_code = item_td[0].select_one("a") or item_td[0]
            item_name = item_td[1].select_one("a") or item_td[1]

            item_code_text = item_code.text
            item_name_text = item_name.text

            if level == 5:
                item_name_text = item_td[2].text

            if item_code.name == "a":
                item_href = item_code.get("href")
                item_code_text = item_code.text
            else:
                item_href = None

            content = f"{item_code_text},{item_name_text},{level},{parent_code}"
            file.write(content + "\n")

            if item_href:
                crawl_next_level(get_url_prefix(url) + item_href, level + 1, item_code_text, file)

if __name__ == '__main__':
    base_url = "http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/index.html"
    province_list = get_html_content(base_url).select('tr.provincetr a')

    with open("area.csv", "w", encoding="utf-8") as file:
        for province in province_list:
            href = province.get("href")
            province_code = href[:2] + "0000000000"
            province_name = province.text

            content = f"{province_code},{province_name},1,0"
            file.write(content + "\n")

            crawl_next_level(get_url_prefix(base_url) + href, 2, province_code, file)
