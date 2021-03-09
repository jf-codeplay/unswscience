import geopandas as gpd
import pandas as pd
import json
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, SingleIntervalTicker, HoverTool, Slider
from bokeh.palettes import brewer
from bokeh.layouts import column
import re


def year_parser(year_string):
    start_year = ""
    end_year = ""
    if len(year_string) == 4:
        start_year = end_year = year_string
    elif len(year_string) > 4:
        if re.search(r"(-|~|–)\s?(\d{2})(?!\d{2})", year_string):  # 1993-95
            start_year = re.search(r"\d{4}", year_string).group(0)
            end_year = start_year[:2] + re.search(r"(?<!\d)(\d{2})(?!\d{2})", year_string).group(0)
        else:
            years = [year.group(0) for year in re.finditer(r"(19|20)\d{2}", year_string)]
            start_year = min(years)
            end_year = max(years)
    new_year_list = list(range(int(start_year), int(end_year)+1))
    return [str(year) for year in new_year_list]


def rename_country(data):
    country_name_dict = {
        'United States': 'United States of America',
        'Korea, Republic of': 'South Korea',
        'Russian Federation': 'Russia',
        'Hong Kong': 'Hong Kong S.A.R.'
    }
    for researcher in data:
        if researcher['experience']:
            for experience in researcher["experience"]:
                experience["country"] = list(set([country_name_dict[country] if country in country_name_dict.keys()
                                                  else country for country in experience["country"]]))
    return data


def year_range(staff_data):
    year_list = []
    for researcher in staff_data:
        if researcher["experience"]:
            for experience in researcher["experience"]:
                for year in experience["year"]:
                    year_list += year_parser(year)
    start_year = min(year_list)
    end_year = max(year_list)
    return str(start_year), str(end_year)


def get_country_list(staff_data):
    total_country_list = []
    for researcher in staff_data:
        if researcher["experience"]:
            for experience in researcher["experience"]:
                total_country_list += experience["country"]
    return list(set(total_country_list))


def get_patch_info(staff_data, start_year, end_year):
    chronicle_data_dict = {}
    total_country_list = get_country_list(staff_data)
    for year in range(int(start_year), int(end_year)+1):
        country_dict = {}
        for country in total_country_list:
            experience_info = []
            for researcher in staff_data:
                if researcher["experience"]:
                    for experience in researcher["experience"]:
                        if len(experience["year"]) == 1 and len(experience["country"]) == 1:
                            #print(str(year), year_parser(experience["year"][0]), year in year_parser(experience["year"][0]), country, experience["country"][0], country == experience["country"][0])
                            if str(year) in year_parser(experience["year"][0]) and country == experience["country"][0]:
                                #print(researcher["name"])
                                experience["name"] = researcher["name"]
                                experience["img"] = researcher["image"].strip(" 1x")
                                experience_info.append(experience)
            people = len(experience_info)
            if people > 0:
                #print("year {} country {} people {}".format(year, country, people))
                experience_df = pd.DataFrame(data={'country': country, 'people': people}, index=[0])
                geo_df = gdf[gdf["country"] == country]
                for i in range(people):
                    column_name_list = ["name", "title", "affiliation", "img"]
                    for name in column_name_list:
                        if type(experience_info[i][name]) == list:
                            experience_df[name+str(i)] = ', '.join(experience_info[i][name])
                        elif type(experience_info[i][name]) == str:
                            experience_df[name + str(i)] = experience_info[i][name]
                merged = geo_df.merge(experience_df, on='country', how='left')
                merged_json = json.loads(merged.to_json())
                country_dict[country] = [json.dumps(merged_json), people]
            elif people == 0:
                country_dict[country] = None
        chronicle_data_dict[str(year)] = country_dict.copy()
    return chronicle_data_dict


def get_tooltips(people):
    def researcher_html(img, name, title, affiliation):
        html = """
        <tr>
          <td>
            <img
                src="{}" height=auto width="42" alt="{}"
                style="float: left; margin: 0px 15px 15px 0px;"
                border="2"
            ></img>
          </td>
          <td>
            <div>
                <span style="font-size: 17px; font-weight: bold;">{}</span>
            </div>
            <div>
                <span style="font-size: 15px;">{}</span>
            </div>
            <div>
                <span style="font-size: 10px; color: #696;">{}</span>
            </div>
          </td>
        </tr>
        """.format(img, img, name, title, affiliation)
        return html
    tooltips = ''
    for i in range(people):
        img = "@img"+str(i)
        name = "@name"+str(i)
        title = "@title"+str(i)
        affiliation = "@affiliation"+str(i)
        tooltips += researcher_html(img, name, title, affiliation)
    return '<table style="width:100%">' + tooltips + '</table>'


def get_country(researcher_dict):
    country_list = []
    if researcher_dict["experience"]:
        for i in researcher_dict["experience"]:
            country_list += i["country"]
    return list(set(country_list))


# Load geographical data
shapefile = "countries_10m/ne_10m_admin_0_countries.shp"
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
# Rename columns
gdf.columns = ['country', 'country_code', 'geometry']
# Remove Antarctica
gdf = gdf.drop(gdf.index[172])
json_file = json.loads(gdf.to_json())
background_json_data = json.dumps(json_file)
geosource = GeoJSONDataSource(geojson = background_json_data)
palette = brewer["OrRd"][8]
palette = palette[::-1]
color_mapper = LinearColorMapper(palette=palette, low=0, high=80, nan_color='#e8e8e8')
ticker = SingleIntervalTicker(interval=10, num_minor_ticks=8)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal', ticker=ticker)
p = figure(title='UNSW STAFF WORLD FOOTPRINT (Faculty of Science)', plot_height=600,
           plot_width=950, toolbar_location="below", tools='pan, reset, wheel_zoom')
p.title.text_font_size = "20pt"
p.title.text_font = "times"
p.title.text_font_style = "italic"
p.title.align = "center"
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.patches('xs', 'ys', source=geosource, line_color='black', line_width=0.25, fill_color="#e8e8e8")

country_counter = 0
number_of_people_list = []
# Load and tidy up researcher data
with open("../staff_data.json", 'r') as f:
    staff_data = json.load(f)
renamed_staff_data = rename_country(staff_data)
country_list = get_country_list(renamed_staff_data)
for country in country_list:
    for researcher in renamed_staff_data:
        if country in get_country(researcher):
            country_counter += 1
    number_of_people_list.append(country_counter)
    country_counter = 0
start_year, end_year = year_range(renamed_staff_data)
df = pd.DataFrame(data={'country': country_list, 'people': number_of_people_list})
# Merge researcher data to geographical data
merged = gdf.merge(df, on='country', how='right')
end_year = "2021"
chronicle_data_dict = get_patch_info(renamed_staff_data, start_year, end_year)
TOOLTIPS = [('Country/region', '@country'), ('People', '@people')]
for country in country_list:
    merged_json = json.loads(merged[merged["country"] == country].to_json())
    json_data = json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson=json_data)
    patch = p.patches('xs', 'ys', source=geosource, fill_color={'field': 'people', 'transform': color_mapper},
                      line_color='black', line_width=0.25, fill_alpha=1, name=country)
    p.add_tools(HoverTool(renderers=[patch], tooltips=TOOLTIPS,
                          toggleable=False,
                          name=country+"hovertool"))
p.add_layout(color_bar, 'below')


def update_plot(attr, old, new):
    year = slider.value
    country_dict = chronicle_data_dict[str(year)]
    p.title.text = 'UNSW STAFF WORLD FOOTPRINT (Faculty of Science) year: {}'.format(year)
    print(year)
    for country in country_list:
        patch = p.select(country)
        hover_tool = p.select(name=country+"hovertool", type=HoverTool)
        print("patch: {}, hover_tool: {}".format(patch, hover_tool))
        if country_dict[country]:
            print("Found data: ", country)
            patch.visible = True
            patch.data_source = GeoJSONDataSource(geojson=country_dict[country][0])
            people = country_dict[country][1]
            hover_tool.tooltips=get_tooltips(people)
        elif not country_dict[country]:
            print("can't find data: ", country)
            patch.visible = False


# Make a slider object: slider
slider = Slider(title = 'Year', start = int(start_year), end = int(end_year), step = 1, value = int(end_year))
slider.on_change('value', update_plot)
layout = column(p, slider)
curdoc().add_root(layout)