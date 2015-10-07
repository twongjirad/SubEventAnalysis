#include "SubEventIO.hh"

namespace subevent {
  
  SubEventIO::SubEventIO( std::string filename, std::string mode_ )
    : mode(mode_) {
    
    subevents = new SubEventList();

    if ( mode=='w' ) {
      fFile = new TFile( filename.c_str(), "RECREATE" );
      defineTree();
    }
  }

  SubEventIO::~SubEventIO() {
  }

  void SubEventIO::defineTree() {
    fTree = new TTree("subevents", "SubEvent Tree");
    //b_subeventlist = new TBranch( "subeventlist", subevents );
    fTree->Branch( "subeventlist", subevents );
  }

  void SubEventIO::transferSubEventList( SubEventList* subeventsrc ) {
    for ( SubEventListIter it=subeventsrc->begin(); it!=subeventsrc->end(); it++ ) {
      subevents->add( std::move( *it ) );
    }
  }

  void SubEventIO::fill() {
    fTree->Fill();
  }

  void SubEventIO::write() {
    fTree->Write();
  }


};
