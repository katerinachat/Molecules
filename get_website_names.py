import requests
import re


people_pages = []
for i in range(36):
    print(i)
    response = requests.get('https://www.turing.ac.uk/people/researchers?_wrapper_format=drupal_ajax&page=' + str(i))
    print(response.status_code)
    # print(response.content)
    people_pages.append(response.content)
    print('--------------')

names = []
for page in people_pages:
    names_one_page = re.findall('/people\\\\\\\\/researchers\\\\\\\\/([^\\\\\\\\]*)\\\\\\\\u0022', str(page))
    names_one_page = list(set(names_one_page))
    names.extend(names_one_page)

names = list(set(names))
with open('ati-names.txt', 'w') as f:
    for name in names:
        f.write(name + '\n')
