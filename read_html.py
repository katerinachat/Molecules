from html.parser import HTMLParser
import requests
from bs4 import BeautifulSoup
import pandas


names = []
with open('ati-names.txt', 'r') as f:
    txt = f.readline()
    while txt:
        names.append(txt.replace('\n', ''))
        txt = f.readline()

# Download websites
websites = {}
for name in names:
    web_page = requests.get('https://www.turing.ac.uk/people/researchers/' + name)
    websites[name] = web_page.text


# Process websites
processed_dict = {}
for name in names:
    web_page_text = websites[name]
    soup = BeautifulSoup(web_page_text, 'html.parser')
    mydivs = soup.findAll("div", {"class": "container"})

    # divs [2] contains what we need
    person_data = {}
    for mydiv in mydivs:
        contents_1 = mydiv.findAll({"div"})
        for content_1 in contents_1:
            content = []
            links = []
            header = content_1.findAll({"h2"})
            para = content_1.findAll({"p"})
            links_extract = content_1.findAll({"a"})
            if len(header) > 0:
                header = header[0].text
                for para_ele in para:
                    content.append(para_ele.text)
                for links_ele in links_extract:
                    links.append(links_ele.text)
                if header == "Research areas":
                    person_data[header] = links
                    continue
                if (header in person_data) is False:
                    person_data[header] = content
    processed_dict[name] = person_data
    print("processed: " + name)

# convert to dataframe
topics = ["Research areas", "Bio", "Research interests", "Achievements and awards", ""]
for name in names:
    data = processed_dict[name]
    for topic in topics:
        data_ele = data[topic]

