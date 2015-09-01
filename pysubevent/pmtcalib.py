import json

def getCalib( jsonfile ):
    
    f = open( jsonfile )
    jspe = json.load( f )

    spe = {}
    for ch in jspe["spe"]:
        #print ch,jspe["spe"][ch]
        spe[ int(ch) ] = int(jspe["spe"][ch])
    return spe

if __name__ == "__main__":
    spe = getCalib( "pmtcalib_20150807.json" )
    print spe
