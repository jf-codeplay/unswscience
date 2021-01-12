import re
import pycountry
import requests
from analysis.stanford_tagger import tagger
import analysis.regex_library as rgx
import json


class ExtractExperience:
    def __init__(self, line, researcher):
        self.line = line
        self.researcher = researcher

    @staticmethod
    def substring_distance(a, b):
        d = min(abs(min(a) - max(b)), abs(min(b) - max(a)))
        return d

    def search_title(self):
        matched_title = []
        for regex in rgx.title_dict.values():
            matched = [name.group(0).strip() for name in re.finditer(regex, self.line)]
            new_matched = []
            for index, title in enumerate(matched):
                if title.lower().endswith("postdoctoral") and index+1 < len(matched):
                    if matched[index+1].lower().startswith("fellow"):
                        new_title = title + ' ' + matched[index+1]
                        new_matched.append(new_title)
                        matched.remove(matched[index+1])
                else:
                    new_matched.append(title)
            matched_title += new_matched
        medical_degree = ["Bachelor of Medicine, Bachelor of Surgery", "MBBS", "MB BS", "BMBS", "MBChB", "MBBCh",
                  "Bachelor of Pharmacy", "B Pharm", "PharmB",
                  "Master of Pharmacy", "MPharm",
                  "Master of Clinical Medicine", "MCM",
                  "Master of Medical Science", "MMSc", "MMedSc",
                  "Master of Medicine", "MMed",
                  "Doctor of Medicine", "Dr.MuD", "Dr.Med",
                  "Doctor of Osteopathic Medicine",
                  "Doctor of Pharmacy", "PharmD"
                  ]
        for degree in medical_degree:
            if degree in self.line:
                matched_title.append(degree)
        if len(matched_title) >= 2:
            matched_title = self.filter_title(matched_title)
        return matched_title

    def filter_title(self, title_list):
        """
        Using Stanford Named Entity Recognizer to remove titles that do not belong to the UNSW researcher.
        Example: She then moved to Princeton University (United States) where she earned a PhD in Chemistry in 2017
        under the mentorship of Professor Emily Carter.
        :param title_list:
        :return:
        """
        #print("Original", title_list)
        named_entities = tagger(self.line)
        other_person_names = [name for name, tag in named_entities if name not in self.researcher]
        for name in other_person_names:
            name = re.sub("[^a-zA-Z\s.]+", "", name)
            matched = re.finditer(name, self.line)
            for m in matched:
                for t in title_list:
                    for title in re.finditer(t, self.line):
                        d = self.substring_distance([title.start(), title.end()], [m.start(), m.end()])
                        if d <= 2:
                            title_list.remove(t)
        #print("After", title_list)
        return title_list

    def search_affiliation(self):
        self.line.replace('\n', ' ')
        matched_affiliation_list = [name.group(0).strip() for name in re.finditer(rgx.uni, self.line)]
        aussie_uni_abbreviation = {"ANU": "Australian National University",
                                   "UNSW": "University of New South Wales",
                                   "USyd": "University of Sydney",
                                   "UTS": "University of Technology Sydney",
                                   "UQ": "University of Queensland",
                                   "RMIT": "Royal Melbourne Institute of Technology"}
        for abbr, full_name in aussie_uni_abbreviation.items():
            if abbr in self.line and full_name not in matched_affiliation_list:
                matched_affiliation_list.append(abbr)
        potential_countries = ["France", "Spain", "Canada", "Germany", "Austria",
                               "Switzerland", "Belgium", "Colombia", "Mexico"]
        for country in self.search_country():
            if country in potential_countries and not matched_affiliation_list:
                print("Try to find some non-English uni... country:{}".format(country))
                non_eng_list = list(self.alternative_search_affiliation())
                matched_affiliation_list = matched_affiliation_list + non_eng_list
        return matched_affiliation_list

    def alternative_search_affiliation(self):
        """
        search for the university/institute names that are not written in English using Hipo university API
        :return: list
        """
        matched_affiliation_list = []
        for name in self.search_country():
            api = "http://universities.hipolabs.com/search?country="+name.lower()
            response = requests.get(api)
            if response.status_code == 404:
                raise Exception("Can't find the country name")
            elif response.status_code == 200:
                for i in response.json():
                    for german, english in [('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('Ä', 'Ae'), ('Ö', 'Oe'), ('Ü', 'Ue')]:
                        i["name"] = i["name"].replace(german, english)
                    if i["name"] in self.line:
                        matched_affiliation_list.append(i["name"])
                        print("!!!!!!!!!!Find some non-English uni names!!!!!!!!!!")
        return matched_affiliation_list

    def search_year(self):
        year_list = [year.group(0) for year in re.finditer(rgx.year, self.line)]
        return year_list

    def search_country(self):
        country_list = []
        for country in pycountry.countries:
            if country.name in self.line:
                country_list.append(country.name)
            # if country.alpha_2 in string:
            #     country_list.append(country.alpha_2)
            # if country.alpha_3 in string:
            #     country_list.append(country.alpha_3)
        return country_list


def process_biography_html(html_text, name):
    html_text = re.sub(rgx.href_link, '', html_text)  # remove html links
    html_text = re.sub(rgx.http_link, '', html_text)  # remove in-text http links
    experience_list = []
    experience = {}
    bio_list = re.split(rgx.html_tag, html_text)
    unwanted_list = ["li", "p", "br", "\n"]
    bio_list = [bio for bio in bio_list if bio not in unwanted_list]
    # bio_list = list(filter(None, bio_list))  # Filter out empty string
    for section in bio_list:
        section_list = re.split(rgx.end_of_sentence, section)
        # section_list = list(filter(None, section_list))  # Filter out empty string
        for line in section_list:
            #print(line)
            #empty_list_counter = 0
            ee = ExtractExperience(line, name)
            title = ee.search_title()
            affiliation = ee.search_affiliation()
            year = ee.search_year()
            country = ee.search_country()
            # for item in [title, affiliation, year, country]:
            #     if not item:
            #         empty_list_counter += 1
            # if empty_list_counter <= 2:
            if title and affiliation:
                #experience["sentence"] = line
                experience["title"] = title
                experience["affiliation"] = affiliation
                experience["year"] = year
                experience["country"] = country
                experience_list.append(experience.copy())
                experience.clear()
                # print("Name: {}\nMatch string:{}\n Title: {}\n Uni: {}\n Year:{}\n Country:{}\n"
                #       .format(i["name"], line, title, affiliation, year, country))
    return experience_list


with open('../output_2021.json', 'r') as f:
    data = json.load(f)
# for i in data:
#     if i["biography"]:
#         i["biography"] = i["biography"].replace('\u00a0', ' ')  # cleaning non-break space
#     if i["qualification"]:
#         i["qualification"] = i["qualification"].replace('\u00a0', ' ')
bio_counter = 0
quali_counter = 0
no_info = 0
after_process = 0
warning = 0
structured_data = []
for i in data:
    if i["name"] == "Professor Dewei Chu":
        personal_experience_dict = {"name": i["name"], "link": i["link"], "experience": []}
        print("="*50)
        if i["biography"]:
            bio_counter += 1
            personal_experience_dict["experience"] += process_biography_html(i["biography"], i["name"])
        if i["qualification"]:
            quali_counter += 1
            personal_experience_dict["experience"] += process_biography_html(i["qualification"], i["name"])
        if i["biography"] is None and i["qualification"] is None:
            no_info += 1
        print(personal_experience_dict)
        structured_data.append(personal_experience_dict.copy())
        if personal_experience_dict["experience"]:
            after_process += 1
        for exp in personal_experience_dict["experience"]:
            if len(exp["title"]) > 1:
                print("WARNING! This experience {} has more than 1 item.".format(exp["title"]))
                warning += 1
            if len(exp["affiliation"]) > 1:
                print("WARNING! This experience {} has more than 1 item.".format(exp["affiliation"]))
                warning += 1
            if len(exp["year"]) > 1:
                print("WARNING! This experience {} has more than 1 item.".format(exp["year"]))
                warning += 1
            if len(exp["country"]) > 1:
                print("WARNING! This experience {} has more than 1 item.".format(exp["year"]))
                warning += 1
        personal_experience_dict.clear()
print("#"*50)
print("Total:{}\nBiography:{}\nQualification:{}\nNo Info:{}".format(len(data), bio_counter, quali_counter, no_info))
print("#"*50)
print("Useful data:{}\nWarning:{}".format(after_process, warning))
print("#"*50)
with open('structured_data.json', 'w') as file:
    json.dump(structured_data, file, indent=4)
