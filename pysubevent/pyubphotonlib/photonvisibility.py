import os,sys
import json
import ROOT as rt
import pyubphotonlib.cyubphotonlib as cyplib

class PhotonVisibility:
    def __init__( self, config_json_file ):

        f = open( config_json_file, 'r' )
        config = json.load( f )

        self.Nx = int(config["Nx"])
        self.Ny = int(config["Ny"])
        self.Nz = int(config["Nz"])
        self.xmin = float(config["xmin"])
        self.xmax = float(config["xmax"])
        self.ymin = float(config["ymin"])
        self.ymax = float(config["ymax"])
        self.zmin = float(config["zmin"])
        self.zmax = float(config["zmax"])

        self.voxeldef = cyplib.PyPhotonVoxelDef( self.xmin, self.xmax, self.Nx, self.ymin, self.ymax, self.Ny, self.zmin, self.zmax, self.Nz )
        self.photonlib = cyplib.PyPhotonLibrary( str(config["datafile"]), self.voxeldef, int(config["NOpChannels"]) )

    def getCounts( pos, opchannel ):
        return self.photonlib.getCounts( pos, opchannel )

    def getVisibility( voxid ):
        pass

    def getVoxel( pos ):
        pass
