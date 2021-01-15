import geopandas as gpd
import pandas as pd
import json
from bokeh.io import save
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, SingleIntervalTicker
from bokeh.palettes import brewer


def get_country(researcher_dict):
    country_list = []
    if researcher_dict["experience"]:
        for i in researcher_dict["experience"]:
            country_list += i["country"]
    return list(set(country_list))


# get data
with open("../staff_data.json", 'r') as f:
    data = json.load(f)
total_country_list = []
country_counter = 0
number_of_people_list = []
for researcher in data:
    total_country_list += get_country(researcher)
total_country_list = list(set(total_country_list))
for country in total_country_list:
    for researcher in data:
        if country in get_country(researcher):
            country_counter += 1
    number_of_people_list.append(country_counter)
    country_counter = 0
df = pd.DataFrame(data={'country': total_country_list, 'people': number_of_people_list})
df = df.replace('United States', 'United States of America')
df = df.replace('Korea, Republic of', 'South Korea')
df = df.replace('Russian Federation', 'Russia')
#print(df)
shapefile = "countries_110m/ne_110m_admin_0_countries.shp"
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
#print(gdf[gdf["country_code"] == "RUS"])
gdf = gdf.drop(gdf.index[159])
merged = gdf.merge(df, on='country', how = 'left')
#print(merged[merged["country"] == "Taiwan"])
merged_json = json.loads(merged.to_json())
json_data = json.dumps(merged_json)
# print(json_data)



#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data)
#Define a sequential multi-hue color palette.
palette = brewer["OrRd"][7]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
#color_mapper = LinearColorMapper(palette = palette, low = 0, high = 60)
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 70, nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
ticker = SingleIntervalTicker(interval = 10, num_minor_ticks=7)
#Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width = 500, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal', ticker = ticker)
#Create figure object.
p = figure(title = 'UNSW Staff World Footprint', plot_height = 600 , plot_width = 950, toolbar_location = None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure.
p.patches('xs','ys', source = geosource, fill_color = {'field' :'people', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify figure layout.
p.add_layout(color_bar, 'below')
save(p)