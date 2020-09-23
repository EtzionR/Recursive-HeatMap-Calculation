from smart_heatmap import HeatMap, loadshp, loadkml, loadcsv


# example 1
xy = loadshp(r'examples\rome_100000.shp')
hm = HeatMap(xy, depth=6)
hm.save_map(r'output\Rome_100000') # shp

# example 2
xy = loadkml(r'examples\Gibraltar.kml')
hm = HeatMap(xy, depth=3)
hm.save_map(r'output\Gibraltar','kml')

# example 3
xy = loadcsv(r'examples\circle.csv','x','y')
hm = HeatMap(xy, depth=4)
hm.save_map(r'output\Circle','csv')

# example 4
xy = loadcsv(r'examples\circle.csv','x','y')
hm = HeatMap(xy, depth=4)
hm.plot()