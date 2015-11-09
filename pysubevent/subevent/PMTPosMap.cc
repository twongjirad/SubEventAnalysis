#include "PMTPosMap.hh"
#include <cstring>

namespace subevent {


  PMTPosMap::PMTPosMap() {

  }

  PMTPosMap::~PMTPosMap() {
  }

  
  bool PMTPosMap::GetPos( int femch, double pos[] ) {

    const double FEMCH[36][3] = { { 2.458 , 55.313 , 951.861 } , // FEMCH00
			       { 2.265 , 55.822 , 911.066 } , // FEMCH01
			       { 2.682 , 27.607 , 989.712 } , // FEMCH02
			       { 1.923 , -0.722 , 865.598 } , // FEMCH03
			       { 2.645 , -28.625 , 990.356 } , // FEMCH04
			       { 2.324 , -56.514 , 951.865 } , // FEMCH05
			       { 2.041 , -56.309 , 911.939 } , // FEMCH06
			       { 1.559 , 55.625 , 751.884 } , // FEMCH07
			       { 1.438 , 55.8 , 711.073 } , // FEMCH08
			       { 1.795 , -0.502 , 796.208 } , // FEMCH09
			       { 1.475 , -0.051 , 664.203 } , // FEMCH10
			       { 1.495 , -56.284 , 751.905 } , // FEMCH11
			       { 1.487 , -56.408 , 711.274 } , // FEMCH12
			       { 1.226 , 55.822 , 540.929 } , // FEMCH13
			       { 1.116 , 55.771 , 500.134 } , // FEMCH14
			       { 1.448 , -0.549 , 585.284 } , // FEMCH15
			       { 1.481 , -0.875 , 453.096 } , // FEMCH16
			       { 1.479 , -56.205 , 540.616 } , // FEMCH17
			       { 1.505 , -56.323 , 500.221 } , // FEMCH18
			       { 0.913 , 54.693 , 328.212 } , // FEMCH19
			       { 0.682 , 54.646 , 287.976 } , // FEMCH20
			       { 1.014 , -0.706 , 373.839 } , // FEMCH21
			       { 0.949 , -0.829 , 242.014 } , // FEMCH22
			       { 1.451 , -57.022 , 328.341 } , // FEMCH23
			       { 1.092 , -56.261 , 287.639 } , // FEMCH24
			       { 0.703 , 55.249 , 128.355 } , // FEMCH25
			       { 0.558 , 55.249 , 87.7605 } , // FEMCH26
			       { 0.665 , 27.431 , 51.1015 } , // FEMCH27
			       { 0.658 , -0.303 , 173.743 } , // FEMCH28
			       { 0.947 , -28.576 , 50.4745 } , // FEMCH29
			       { 0.8211 , -56.203 , 128.179 } , // FEMCH30
			       { 0.862 , -56.615 , 87.8695 } , // FEMCH31
			       { -161.3 , -2.355 , 760.575 } , // FEMCH32
			       { -161.3 , -2.7 , 550.333 } , // FEMCH33
			       { -161.3 , -2.594 , 490.501 } , // FEMCH34
			       { -161.3 , -2.801 , 280.161 } };// FEMCH35
    
    if (femch<0 && femch>=36 ) {
      std::memset( pos, 0, sizeof(double)*3 );
      return false;
    }
    for (int i=0; i<3; i++)
      pos[i] = FEMCH[femch][i];
    return true;
  }

  bool PMTPosMap::GetPos( int femch, std::vector<double>& pos) {

    double pos_[3];
    GetPos( femch, pos_ );
    
    pos.resize(3);
    if (femch<0 && femch>=36 ) {
      for (int i=0; i<3; i++)
	pos.at(i) = 0;
      return false;
    }
    
    for (int i=0; i<3; i++)
      pos[i] = pos_[i];

    return true;
  }
  
}
