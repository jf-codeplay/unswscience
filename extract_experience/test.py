import json
import requests


def get_country(researcher_dict):
    country_list = []
    if researcher_dict["experience"]:
        for i in researcher_dict["experience"]:
            country_list += i["country"]
    return list(set(country_list))


with open("../staff_data.json", 'r') as f:
    data = json.load(f)
total_country_list = []
country_counter = 0
country_number_list = []
# for researcher in data:
#     if researcher["experience"]:
#         for i in researcher["experience"]:
#             if "China" in i["country"]:
#                 print(researcher["name"], i)
for researcher in data:
    total_country_list += get_country(researcher)
total_country_list = list(set(total_country_list))
for country in total_country_list:
    for researcher in data:
        if country in get_country(researcher):
            country_counter += 1
    country_number_list.append(country_counter)
    country_counter = 0
for i in range(len(total_country_list)):
    print("country:{}, number:{}".format(total_country_list[i], country_number_list[i]))
print(len(total_country_list))
#
# warning = 0
# name = []
# for i in data:
#     if i["experience"]:
#         for j in i["experience"]:
#             len_title = len(j["title"])
#             len_country = len(j["country"])
#             len_affiliation = len(j["affiliation"])
#             len_year = len(j["year"])
#             if len_title != len_affiliation or len_title != len_year:
#                 print(i)
#                 name.append(i["name"])
#                 warning += 1
# print(warning)
# print(len(list(set(name))))