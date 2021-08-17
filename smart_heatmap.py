# Create by Etzion Harari
# https://github.com/EtzionR

# Load libraries:
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from simplekml import Kml
import shapefile as shp
import pandas as pd
import numpy as np

COL = ['b3006100','b300803c','b300a16b','b300c4a4','b300ebdf','b300eaff','b300bbff','b30091ff','b30062ff','b30022ff']

PRJ = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],' \
      'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["EGM96_Geoid",' \
      'VDATUM["EGM96_Geoid"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]'

GEO = '				<coordinates>'

KML = 'kml'
SHP = 'shp'
CSV = 'csv'

class Square:
    """
    simple square in the heatmap
    """
    def __init__(self,x_min,y_min,x_max,y_max,level):
        """
        square parameters
        :param x_min: x minimum
        :param y_min: y minimum
        :param x_max: x maximum
        :param y_max: y maximum
        :param level: square current depth
        """
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_mid =(x_max+x_min)/2
        self.y_mid =(y_max+y_min)/2
        self.count = 0
        self.level = level

    def split(self):
        """
        split the square to 4 small squares
        :return: 4 small squares
        """
        return [Square(self.x_min, self.y_min, self.x_mid, self.y_mid, self.level+1),
                Square(self.x_mid, self.y_mid, self.x_max, self.y_max, self.level+1),
                Square(self.x_min, self.y_mid, self.x_mid, self.y_max, self.level+1),
                Square(self.x_mid, self.y_min, self.x_max, self.y_mid, self.level+1)]

    def count_point(self, value):
        """
        define the point count value
        :param value: input value
        """
        self.count = value

    def get_coordinates(self):
        """
        get the square xy coordinates
        :return: square xy coordinates
        """
        return [(self.x_min, self.y_min),
                (self.x_max, self.y_min),
                (self.x_max, self.y_max),
                (self.x_min, self.y_max),
                (self.x_min, self.y_min)]

class HeatMap:
    """
    HeatMap calculation object
    """
    def __init__(self, data, depth):
        """
        initialize the heatmap parameters
        :param data: list of xy tuples
        :param depth: required square depth
        """
        self.depth = depth
        self.xy = data
        self.x = [x for x,_ in self.xy]
        self.y = [y for _,y in self.xy]
        self.x_min, self.y_min = min(self.x), min(self.y)
        self.x_max, self.y_max = max(self.x), max(self.y)
        self.x_len = self.x_max-self.x_min
        self.y_len = self.y_max-self.y_min
        self.side = min(self.x_len, self.y_len)/2
        self.col, self.row = self.length_width()
        self.squares = self.initialize_squares()
        self.heatmap = self.square_intersection()

    def square_intersection(self):
        """
        calculate the count of the intersection
        between the square to the given points
        :return: squares with count value
        """
        hm = []
        for s in self.squares:
            self.recursive_intersect(self.xy, s, hm)
        return hm

    def recursive_intersect(self, xy, square, hm):
        """
        recursive function for intersections calculte
        :param xy: input xy-sub-list
        :param square: input square boundary
        :param hm: final square list
        """
        sub = [(x,y) for x,y in xy if square.x_min <=x<=square.x_max
                                  and square.y_min <=y<=square.y_max]
        if len(sub)==0:
            return
        elif square.level==self.depth:
            square.count_point(len(sub))
            hm.append(square)
            return
        else:
            for s in square.split():
                self.recursive_intersect(sub,s,hm)

    def initialize_squares(self):
        """
        create the first square layer
        :return: squares objects list
        """
        squares = []
        for i in range(self.col):
            lower_x = self.x_min + (i * self.side)
            upper_x = lower_x + self.side
            for j in range(self.row):
                lower_y = self.y_min + (j * self.side)
                upper_y = lower_y + self.side
                squares.append(Square(lower_x, lower_y, upper_x, upper_y, 0))
        return squares

    def length_width(self):
        """
        calculate the length & width of the extent
        :return: length and width values
        """
        col = int(self.x_len//self.side)
        row = int(self.y_len//self.side)
        if self.x_len > self.y_len:
            return col+1, row
        elif self.x_len < self.y_len:
            return col, row+1
        else:
            return col, row

    def plot(self,size=6):
        """
        plot the heatmap results
        """
        fig, ax = plt.subplots(1, 1, figsize=((self.col / max(self.col, self.row)) * size,
                                              (self.row / max(self.col, self.row)) * size))
        fig.suptitle(f'HeatMap Output\n(depth={self.depth}, number of points={len(self.xy)})')
        p = PatchCollection([Polygon(s.get_coordinates(), True) for s in self.heatmap], cmap='autumn')
        p.set_array(np.array([s.count for s in self.heatmap]))
        ax.add_collection(p)

        ax.set_xlim(self.x_min, self.x_max)
        ax.set_ylim(self.y_min, self.y_max)
        fig.colorbar(p, ax=ax)

        plt.savefig(f'HeatMap_Output_depth={self.depth}_number_of_points={len(self.xy)}.png')
        plt.show()

    def save_map(self,filename, format=SHP):
        """
        save the heatmap results to file
        :param filename: name of the file
        :param format: file format (default: shp)
        """
        if format==KML:
            self.create_kml(filename)
        elif format==SHP:
            self.create_shp(filename)
        elif format==CSV:
            self.create_csv(filename)

    def create_kml(self,name):
        """
        create kml file from the HeatMap results
        :param name: filename
        """
        file = Kml()
        counts = [s.count**0.5 for s in self.heatmap]
        c_min, c_max = min(counts), max(counts)
        divisor= (c_max-c_min)/9
        for s in self.heatmap:
            single = file.newpolygon(name=str(s.count),
                                     outerboundaryis=s.get_coordinates())
            single.style.polystyle.color = COL[int(((s.count**0.5)-c_min)//divisor)]

        file.save(name+'.kml')

    def create_csv(self,name):
        """
        create csv file from the HeatMap results
        :param name: filename
        """
        lst=[]
        for s in self.heatmap:
            lst.append((s.level, s.count, s.x_min, s.y_min, s.x_max, s.y_max))
        pd.DataFrame(lst, columns=['depth', 'count', 'x_min', 'y_min', 'x_max', 'y_max']).to_csv(name+'.csv')

    def create_shp(self,name):
        """
        create shapefile from the HeatMap results
        :param name: filename
        """
        layer = shp.Writer(name+'.shp')
        layer.field('level', 'N')
        layer.field('count', 'N')
        for s in self.heatmap:
            layer.poly([s.get_coordinates()])
            layer.record(s.level, s.count)
        layer.close()

        with open(name + '.prj', 'w+', encoding='utf-8') as prj:
            prj.write(PRJ)
            prj.close()

def loadkml(file):
    """
    load the kml file and convert the coordinates to new list
    :param file: path to the kml
    :return: xy-taple list
    """
    lst=[]
    kml = open(file, 'r', encoding='utf-8').read().split('\n')
    for line in kml:
        if GEO in line:
            x,y = line[len(GEO):].split(',')[:2]
            lst.append((float(x),float(y)))
    return lst

def loadshp(file):
    """
    load the shapefile and convert the coordinates to new list
    :param file: path to the shapefile
    :return: xy-taple list
    """
    data = shp.Reader(file)
    return [geo['geometry']['coordinates'] for geo in data.__geo_interface__['features']]

def loadcsv(file,x,y):
    """
    load the csv file and convert the coordinates to new list
    :param file: path to the csv
    :return: xy-taple list
    """
    df = pd.read_csv(file)
    x,y= list(df[x]),list(df[y])
    return [(x[i], y[i]) for i in range(len(x))]


# License
# MIT © Etzion Harari
