pmtposmap = {
    0:[0.558, 55.249, 87.7605],
    1:[0.703, 55.249, 128.355],
    2:[0.665, 27.431, 51.1015],
    3:[0.658, -0.303, 173.743],
    4:[0.947, -28.576, 50.4745],
    5:[0.862, -56.615, 87.8695],
    6:[0.8211, -56.203, 128.179],
    7:[0.682, 54.646, 287.976],
    8:[0.913, 54.693, 328.212],
    9:[0.949, -0.829, 242.014],
    10:[1.014, -0.706, 373.839],
    11:[1.092, -56.261, 287.639],
    12:[1.451, -57.022, 328.341],
    13:[1.116, 55.771, 500.134],
    14:[1.226, 55.822, 540.929],
    15:[1.481, -0.875, 453.096],
    16:[1.448, -0.549, 585.284],
    17:[1.505, -56.323, 500.221],
    18:[1.479, -56.205, 540.616],
    19:[1.438, 55.8, 711.073],
    20:[1.559, 55.625, 751.884],
    21:[1.475, -0.051, 664.203],
    22:[1.795, -0.502, 796.208],
    23:[1.487, -56.408, 711.274],
    24:[1.495, -56.284, 751.905],
    25:[2.265, 55.822, 911.066],
    26:[2.458, 55.313, 951.861],
    27:[2.682, 27.607, 989.712],
    28:[1.923, -0.722, 865.598],
    29:[2.645, -28.625, 990.356],
    30:[2.041, -56.309, 911.939],
    31:[2.324, -56.514, 951.865]
}

def getPosFromID( id ):
    if id in pmtposmap:
        return pmtposmap[id]
    return None

def getDetectorCenter():
    return (125.0,0.5*(-57.022+55.8),0.5*(990.356+51.1015))

if __name__ == "__main__":
    for ich in range(0,36):
        print ich,(pmtpos[ich][0],pmtpos[ich][1],pmtpos[ich][2]+518.0)

