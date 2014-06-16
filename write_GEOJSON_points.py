import geojson 
import json
import csv
import ast

def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

LAT_DEG_P_M = (40.727740 - 40.726840)/100
LON_DEG_P_M = (-73.978720 - -73.979907 )/100

#my_point = geojson.Point((43.24, -1.532))
json_data = open('man_brook.json')
man_brook = json.load(json_data)
json_data.close()

poly_list = []
man_brook_features = man_brook['features']
for polys in man_brook_features:
	cur_poly = polys['geometry']['coordinates'][0]
	poly_list.append([tuple(l) for l in cur_poly])



opacity_list = []
my_feature_list = []
count = 0
with open('data.csv', 'rb') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		row_line = row
		if count >0 and row_line[0]:
			cur_lat = ast.literal_eval(row_line[4])
			cur_lon = ast.literal_eval(row_line[5])	
			valid = 0
			for test_poly in poly_list:
				if  point_in_poly(cur_lon,cur_lat,test_poly):
					valid = 1
					break

			if valid == 1:


				cur_score = ast.literal_eval(row_line[0])/5.0
				lon_step = LON_DEG_P_M*(((cur_score**3)*50+1)*1)
				lat_step = LAT_DEG_P_M*(((cur_score**3)*50+1)*1)
				#my_poly = geojson.Polygon([[(cur_lon - lon_step, cur_lat + lat_step), (cur_lon + lon_step, cur_lat + lat_step), (cur_lon + lon_step, cur_lat - lat_step), (cur_lon - lon_step, cur_lat - lat_step)]])
				my_point = geojson.Point((cur_lon, cur_lat))
				prop_dict = {}
				prop_dict['marker'] = "circle"
				if cur_score < 0.6:
					prop_dict['marker-size'] = "small"
				elif cur_score < 0.8:
					prop_dict['marker-size'] = "medium"
				else:
					prop_dict['marker-size'] = "large"
				prop_dict['marker-color'] = "#FF0000"
				prop_dict['name'] = row_line[1]
				prop_dict['rating'] = str(cur_score*5)
				my_feature = geojson.Feature(geometry=my_point,properties = prop_dict)
				my_feature_list.append(my_feature)
			
		count +=1

my_feature_coll = geojson.FeatureCollection(my_feature_list )


dump = geojson.dumps(my_feature_coll, sort_keys=True)

with open("man_brook_coffee_points.json", "w") as outfile:
	json.dump(my_feature_coll, outfile, indent=4)