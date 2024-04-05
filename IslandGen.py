from PIL import Image
import opensimplex as SIMPLEX
from random import randint
from math import pi, cos, pow
 

class Color:

    def __init__(self, r:int=0, g:int=0, b:int=0, a:int=0):
        self.R = r
        self.G = g
        self.B = b
        self.A = a
    
    def __add__(self, other):
        return Color(self.R + other.R, self.G + other.G, self.B + other.B, self.A + other.A)
    
    def byScalar(self, s):
        return Color(self.R*s, self.G*s, self.B*s, self.A*s)

    
    def getColorVector(self):
        return( (int(self.R), int(self.G), int(self.B), int(self.A)) )




def saveImage(img:Image):
    img.save(f'./output_{RES}_{SIMPLEX.get_seed()}.png')

def valueToColor(color:tuple):
    return (int(color[0]), int(color[1]), int(color[2]), int(color[3]))

def tupleByScalar(color:tuple, a:float):
    return (color[0]*a, color[1]*a, color[2]*a, color[3]*a, )

def clampMap(map, border_left, border_right): 
    ret_map = []
    MIN = 1
    MAX = 0

    for line in map:
        local_min = min(line)
        local_max = max(line)
        if local_max > MAX:
            MAX = local_max
        if local_min < MIN:
            MIN = local_min

    for line in map:
        blankLine = []
        for val in line :
            blankLine.append(border_left + (val-MIN)/(MAX-MIN)*(border_right-border_left))
        ret_map.append(blankLine)
    return ret_map


def addFalloffMap(map):
    newMap = []
    for y in range(RES):
        line = []
        for x in range(RES):
            val = map[y][x] -1 + FALLOFF_STRENGHT* pow(cos(pi/2*((x/RES*2)-1)),FALLOFF_SLOPE) * pow(cos(pi/2*((y/RES*2)-1)),FALLOFF_SLOPE)
            if val < 0 :
                val = 0
            elif val > 1:
                val = 1
            line.append(val)
        newMap.append(line)
    return newMap


def Lerp(t:float, start_value, end_value):
    return start_value + (end_value-start_value)*t






if __name__== '__main__':

# Image Parameters
    IMG_SIZE = 1280
    RES = 128
    SHOW_HEIGHTMAP = False

# Noise Parameters
    N_LAYERS = 6
    OCTAVE = 3
    GAIN = 0.5
    LACUNARITY = 2

    SEED = 69420
    RANDOM_SEED = False

# Terrain Parameters
    
    FALLOFF_STRENGHT = 0
    FALLOFF_SLOPE = 0.5

    WHITE = Color(255,255,255,255)
    BLACK = Color(0,0,0,0)
    ERROR_COLOR = Color(255,255,0,255)

    DEEP_SEA_COLOR = Color(0, 12, 92,255)

    SEA_COLOR = Color(0, 22, 107,255)
    SEA_LEVEL      = 0.1

    WATER_COLOR    = Color(0, 75, 133, 255)
    WATER_LEVEL    = 0.4

    BEACH_COLOR    = Color(254, 255, 214, 255)
    BEACH_LEVEL    = 0.42

    SAND_COLOR     = Color(224, 227, 138, 255)
    SAND_LEVEL     = 0.5

    LAND_COLOR     = Color(83, 207, 0, 255)
    LAND_LEVEL     = 0.55

    TREE_COLOR     = Color(32, 87, 40, 255)
    TREE_LEVEL     = 0.75

    ROCKS_COLOR    = Color(8, 48, 31, 255)
    ROCKS_LEVEL    = 0.8


    MOUNTAIN_COLOR = Color(41, 21, 16, 255)
    MOUNTAIN_LEVEL = 0.85

    TOPS_COLOR = Color(51, 43, 41, 255)
    TOPS_LEVEL = 0.98



    terrain_layers = [0             , SEA_LEVEL, WATER_LEVEL, BEACH_LEVEL, SAND_LEVEL, LAND_LEVEL, TREE_LEVEL, ROCKS_LEVEL, MOUNTAIN_LEVEL, TOPS_LEVEL,     1]
    terrain_colors = [DEEP_SEA_COLOR, SEA_COLOR, WATER_COLOR, BEACH_COLOR, SAND_COLOR, LAND_COLOR, TREE_COLOR, ROCKS_COLOR, MOUNTAIN_COLOR, TOPS_COLOR, WHITE]




# Calculating Noise Layers
    if RANDOM_SEED:
        SIMPLEX.seed(randint(0,9999999999999))
    else:
        SIMPLEX.seed(SEED)
    frequencies = []
    strenghts  = []
    a = 1
    o = OCTAVE
    for n in range(N_LAYERS):
        frequencies.append(o)
        o *= LACUNARITY
        strenghts.append(a)
        a *= GAIN

# Calculating Heights
    heightmap = []
    for j in range(RES):
        line = []
        for i in range(RES):
            value = 0
            for n in range(N_LAYERS):
                value += strenghts[n] * SIMPLEX.noise2(x= frequencies[n]*i/RES, y= frequencies[n]*j/RES)
            line.append(value)
        heightmap.append(line)
    heightmap = clampMap(heightmap,0,1)
    if FALLOFF_STRENGHT > 0:
        heightmap = addFalloffMap(heightmap)

# Calculating Pixels
    pixels = []
    for line in heightmap:
        for px in range(int(IMG_SIZE/RES)):
            for value in line:


                if SHOW_HEIGHTMAP:
                    interpolated_color = BLACK.byScalar(1-value) + WHITE.byScalar(value)
                else:
                    interpolated_color = BLACK
                    for l in range(len(terrain_layers)-1):
                        weight = 0

                        left  = (value - terrain_layers[l])
                        right = (terrain_layers[l+1] - value)

                        if left < 0 or right <0:
                            weight = 0
                        else:
                            weight = (left/(terrain_layers[l+1] - terrain_layers[l]))
                            interpolated_color += terrain_colors[l].byScalar(1-weight) + terrain_colors[l+1].byScalar(weight)

                
                color = interpolated_color.getColorVector()

                for py in range(int(IMG_SIZE/RES)):
                    pixels.append(color)

    
    image = Image.new('RGB', (IMG_SIZE, IMG_SIZE))
    image.putdata(pixels)

    image.show()
    saveImage(image)







