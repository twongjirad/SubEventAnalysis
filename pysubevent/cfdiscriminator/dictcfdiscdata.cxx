//
// File generated by rootcint at Thu Oct  1 14:48:23 2015

// Do NOT change. Changes will be lost next time file is generated
//

#define R__DICTIONARY_FILENAME pysubeventdIcfdiscriminatordIdictcfdiscdata
#include "RConfig.h" //rootcint 4834
#if !defined(R__ACCESS_IN_SYMBOL)
//Break the privacy of classes -- Disabled for the moment
#define private public
#define protected public
#endif

// Since CINT ignores the std namespace, we need to do so in this file.
namespace std {} using namespace std;
#include "dictcfdiscdata.h"

#include "TClass.h"
#include "TBuffer.h"
#include "TMemberInspector.h"
#include "TInterpreter.h"
#include "TVirtualMutex.h"
#include "TError.h"

#ifndef G__ROOT
#define G__ROOT
#endif

#include "RtypesImp.h"
#include "TIsAProxy.h"
#include "TFileMergeInfo.h"

// Direct notice to TROOT of the dictionary's loading.
namespace {
   static struct DictInit {
      DictInit() {
         ROOT::RegisterModule();
      }
   } __TheDictionaryInitializer;
}

// START OF SHADOWS

namespace ROOTShadow {
   namespace Shadow {
   } // of namespace Shadow
} // of namespace ROOTShadow
// END OF SHADOWS

namespace ROOTDict {
   void cfdcLcLCFDFire_ShowMembers(void *obj, TMemberInspector &R__insp);
   static void *new_cfdcLcLCFDFire(void *p = 0);
   static void *newArray_cfdcLcLCFDFire(Long_t size, void *p);
   static void delete_cfdcLcLCFDFire(void *p);
   static void deleteArray_cfdcLcLCFDFire(void *p);
   static void destruct_cfdcLcLCFDFire(void *p);
   static void streamer_cfdcLcLCFDFire(TBuffer &buf, void *obj);

   // Function generating the singleton type initializer
   static ROOT::TGenericClassInfo *GenerateInitInstanceLocal(const ::cfd::CFDFire*)
   {
      ::cfd::CFDFire *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TInstrumentedIsAProxy< ::cfd::CFDFire >(0);
      static ::ROOT::TGenericClassInfo 
         instance("cfd::CFDFire", ::cfd::CFDFire::Class_Version(), "./pysubevent/cfdiscriminator/CFDFire.hh", 7,
                  typeid(::cfd::CFDFire), ::ROOT::DefineBehavior(ptr, ptr),
                  &::cfd::CFDFire::Dictionary, isa_proxy, 0,
                  sizeof(::cfd::CFDFire) );
      instance.SetNew(&new_cfdcLcLCFDFire);
      instance.SetNewArray(&newArray_cfdcLcLCFDFire);
      instance.SetDelete(&delete_cfdcLcLCFDFire);
      instance.SetDeleteArray(&deleteArray_cfdcLcLCFDFire);
      instance.SetDestructor(&destruct_cfdcLcLCFDFire);
      instance.SetStreamerFunc(&streamer_cfdcLcLCFDFire);
      return &instance;
   }
   ROOT::TGenericClassInfo *GenerateInitInstance(const ::cfd::CFDFire*)
   {
      return GenerateInitInstanceLocal((::cfd::CFDFire*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const ::cfd::CFDFire*)0x0); R__UseDummy(_R__UNIQUE_(Init));
} // end of namespace ROOTDict

      namespace cfd {
//______________________________________________________________________________
atomic_TClass_ptr CFDFire::fgIsA(0);  // static to hold class pointer

//______________________________________________________________________________
const char *CFDFire::Class_Name()
{
   return "cfd::CFDFire";
}

//______________________________________________________________________________
const char *CFDFire::ImplFileName()
{
   return ::ROOTDict::GenerateInitInstanceLocal((const ::cfd::CFDFire*)0x0)->GetImplFileName();
}

//______________________________________________________________________________
int CFDFire::ImplFileLine()
{
   return ::ROOTDict::GenerateInitInstanceLocal((const ::cfd::CFDFire*)0x0)->GetImplFileLine();
}

//______________________________________________________________________________
void CFDFire::Dictionary()
{
   fgIsA = ::ROOTDict::GenerateInitInstanceLocal((const ::cfd::CFDFire*)0x0)->GetClass();
}

//______________________________________________________________________________
TClass *CFDFire::Class()
{
   if (!fgIsA) { R__LOCKGUARD2(gCINTMutex); if(!fgIsA) {fgIsA = ::ROOTDict::GenerateInitInstanceLocal((const ::cfd::CFDFire*)0x0)->GetClass();} }
   return fgIsA;
}

} // namespace cfd
      namespace cfd {
//______________________________________________________________________________
void CFDFire::Streamer(TBuffer &R__b)
{
   // Stream an object of class cfd::CFDFire.

   //This works around a msvc bug and should be harmless on other platforms
   typedef ::cfd::CFDFire thisClass;
   UInt_t R__s, R__c;
   if (R__b.IsReading()) {
      Version_t R__v = R__b.ReadVersion(&R__s, &R__c); if (R__v) { }
      TObject::Streamer(R__b);
      R__b >> tfire;
      R__b >> maxamp;
      R__b >> tmax;
      R__b >> maxdiff;
      R__b.CheckByteCount(R__s, R__c, thisClass::IsA());
   } else {
      R__c = R__b.WriteVersion(thisClass::IsA(), kTRUE);
      TObject::Streamer(R__b);
      R__b << tfire;
      R__b << maxamp;
      R__b << tmax;
      R__b << maxdiff;
      R__b.SetByteCount(R__c, kTRUE);
   }
}

} // namespace cfd
//______________________________________________________________________________
      namespace cfd {
void CFDFire::ShowMembers(TMemberInspector &R__insp)
{
      // Inspect the data members of an object of class cfd::CFDFire.
      TClass *R__cl = ::cfd::CFDFire::IsA();
      if (R__cl || R__insp.IsA()) { }
      R__insp.Inspect(R__cl, R__insp.GetParent(), "tfire", &tfire);
      R__insp.Inspect(R__cl, R__insp.GetParent(), "maxamp", &maxamp);
      R__insp.Inspect(R__cl, R__insp.GetParent(), "tmax", &tmax);
      R__insp.Inspect(R__cl, R__insp.GetParent(), "maxdiff", &maxdiff);
      TObject::ShowMembers(R__insp);
}

} // namespace cfd
namespace ROOTDict {
   // Wrappers around operator new
   static void *new_cfdcLcLCFDFire(void *p) {
      return  p ? new(p) ::cfd::CFDFire : new ::cfd::CFDFire;
   }
   static void *newArray_cfdcLcLCFDFire(Long_t nElements, void *p) {
      return p ? new(p) ::cfd::CFDFire[nElements] : new ::cfd::CFDFire[nElements];
   }
   // Wrapper around operator delete
   static void delete_cfdcLcLCFDFire(void *p) {
      delete ((::cfd::CFDFire*)p);
   }
   static void deleteArray_cfdcLcLCFDFire(void *p) {
      delete [] ((::cfd::CFDFire*)p);
   }
   static void destruct_cfdcLcLCFDFire(void *p) {
      typedef ::cfd::CFDFire current_t;
      ((current_t*)p)->~current_t();
   }
   // Wrapper around a custom streamer member function.
   static void streamer_cfdcLcLCFDFire(TBuffer &buf, void *obj) {
      ((::cfd::CFDFire*)obj)->::cfd::CFDFire::Streamer(buf);
   }
} // end of namespace ROOTDict for class ::cfd::CFDFire

/********************************************************
* pysubevent/cfdiscriminator/dictcfdiscdata.cxx
* CAUTION: DON'T CHANGE THIS FILE. THIS FILE IS AUTOMATICALLY GENERATED
*          FROM HEADER FILES LISTED IN G__setup_cpp_environmentXXX().
*          CHANGE THOSE HEADER FILES AND REGENERATE THIS FILE.
********************************************************/

#ifdef G__MEMTEST
#undef malloc
#undef free
#endif

#if defined(__GNUC__) && __GNUC__ >= 4 && ((__GNUC_MINOR__ == 2 && __GNUC_PATCHLEVEL__ >= 1) || (__GNUC_MINOR__ >= 3))
#pragma GCC diagnostic ignored "-Wstrict-aliasing"
#endif

extern "C" void G__cpp_reset_tagtabledictcfdiscdata();

extern "C" void G__set_cpp_environmentdictcfdiscdata() {
  G__add_compiledheader("TObject.h");
  G__add_compiledheader("TMemberInspector.h");
  G__add_compiledheader("CFDFire.hh");
  G__cpp_reset_tagtabledictcfdiscdata();
}
#include <new>
extern "C" int G__cpp_dllrevdictcfdiscdata() { return(30051515); }

/*********************************************************
* Member function Interface Method
*********************************************************/

/* cfd::CFDFire */
static int G__dictcfdiscdata_169_0_1(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
   cfd::CFDFire* p = NULL;
   char* gvp = (char*) G__getgvp();
   int n = G__getaryconstruct();
   if (n) {
     if ((gvp == (char*)G__PVOID) || (gvp == 0)) {
       p = new cfd::CFDFire[n];
     } else {
       p = new((void*) gvp) cfd::CFDFire[n];
     }
   } else {
     if ((gvp == (char*)G__PVOID) || (gvp == 0)) {
       p = new cfd::CFDFire;
     } else {
       p = new((void*) gvp) cfd::CFDFire;
     }
   }
   result7->obj.i = (long) p;
   result7->ref = (long) p;
   G__set_tagnum(result7,G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire));
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_2(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 85, (long) cfd::CFDFire::Class());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_3(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 67, (long) cfd::CFDFire::Class_Name());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_4(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 115, (long) cfd::CFDFire::Class_Version());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_5(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      cfd::CFDFire::Dictionary();
      G__setnull(result7);
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_9(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      ((cfd::CFDFire*) G__getstructoffset())->StreamerNVirtual(*(TBuffer*) libp->para[0].ref);
      G__setnull(result7);
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_10(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 67, (long) cfd::CFDFire::DeclFileName());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_11(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 105, (long) cfd::CFDFire::ImplFileLine());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_12(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 67, (long) cfd::CFDFire::ImplFileName());
   return(1 || funcname || hash || result7 || libp) ;
}

static int G__dictcfdiscdata_169_0_13(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
      G__letint(result7, 105, (long) cfd::CFDFire::DeclFileLine());
   return(1 || funcname || hash || result7 || libp) ;
}

// automatic copy constructor
static int G__dictcfdiscdata_169_0_14(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)

{
   cfd::CFDFire* p;
   void* tmp = (void*) G__int(libp->para[0]);
   p = new cfd::CFDFire(*(cfd::CFDFire*) tmp);
   result7->obj.i = (long) p;
   result7->ref = (long) p;
   G__set_tagnum(result7,G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire));
   return(1 || funcname || hash || result7 || libp) ;
}

// automatic destructor
typedef cfd::CFDFire G__TcfdcLcLCFDFire;
static int G__dictcfdiscdata_169_0_15(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
   char* gvp = (char*) G__getgvp();
   long soff = G__getstructoffset();
   int n = G__getaryconstruct();
   //
   //has_a_delete: 1
   //has_own_delete1arg: 0
   //has_own_delete2arg: 0
   //
   if (!soff) {
     return(1);
   }
   if (n) {
     if (gvp == (char*)G__PVOID) {
       delete[] (cfd::CFDFire*) soff;
     } else {
       G__setgvp((long) G__PVOID);
       for (int i = n - 1; i >= 0; --i) {
         ((cfd::CFDFire*) (soff+(sizeof(cfd::CFDFire)*i)))->~G__TcfdcLcLCFDFire();
       }
       G__setgvp((long)gvp);
     }
   } else {
     if (gvp == (char*)G__PVOID) {
       delete (cfd::CFDFire*) soff;
     } else {
       G__setgvp((long) G__PVOID);
       ((cfd::CFDFire*) (soff))->~G__TcfdcLcLCFDFire();
       G__setgvp((long)gvp);
     }
   }
   G__setnull(result7);
   return(1 || funcname || hash || result7 || libp) ;
}

// automatic assignment operator
static int G__dictcfdiscdata_169_0_16(G__value* result7, G__CONST char* funcname, struct G__param* libp, int hash)
{
   cfd::CFDFire* dest = (cfd::CFDFire*) G__getstructoffset();
   *dest = *(cfd::CFDFire*) libp->para[0].ref;
   const cfd::CFDFire& obj = *dest;
   result7->ref = (long) (&obj);
   result7->obj.i = (long) (&obj);
   return(1 || funcname || hash || result7 || libp) ;
}


/* Setting up global function */

/*********************************************************
* Member function Stub
*********************************************************/

/* cfd::CFDFire */

/*********************************************************
* Global function Stub
*********************************************************/

/*********************************************************
* Get size of pointer to member function
*********************************************************/
class G__Sizep2memfuncdictcfdiscdata {
 public:
  G__Sizep2memfuncdictcfdiscdata(): p(&G__Sizep2memfuncdictcfdiscdata::sizep2memfunc) {}
    size_t sizep2memfunc() { return(sizeof(p)); }
  private:
    size_t (G__Sizep2memfuncdictcfdiscdata::*p)();
};

size_t G__get_sizep2memfuncdictcfdiscdata()
{
  G__Sizep2memfuncdictcfdiscdata a;
  G__setsizep2memfunc((int)a.sizep2memfunc());
  return((size_t)a.sizep2memfunc());
}


/*********************************************************
* virtual base class offset calculation interface
*********************************************************/

   /* Setting up class inheritance */

/*********************************************************
* Inheritance information setup/
*********************************************************/
extern "C" void G__cpp_setup_inheritancedictcfdiscdata() {

   /* Setting up class inheritance */
   if(0==G__getnumbaseclass(G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire))) {
     cfd::CFDFire *G__Lderived;
     G__Lderived=(cfd::CFDFire*)0x1000;
     {
       TObject *G__Lpbase=(TObject*)G__Lderived;
       G__inheritance_setup(G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire),G__get_linked_tagnum(&G__dictcfdiscdataLN_TObject),(long)G__Lpbase-(long)G__Lderived,1,1);
     }
   }
}

/*********************************************************
* typedef information setup/
*********************************************************/
extern "C" void G__cpp_setup_typetabledictcfdiscdata() {

   /* Setting up typedef entry */
   G__search_typename2("Version_t",115,-1,0,-1);
   G__setnewtype(-1,"Class version identifier (short)",0);
   G__search_typename2("vector<ROOT::TSchemaHelper>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR),0,-1);
   G__setnewtype(-1,NULL,0);
   G__search_typename2("reverse_iterator<const_iterator>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgRcLcLiteratorgR),0,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR));
   G__setnewtype(-1,NULL,0);
   G__search_typename2("reverse_iterator<iterator>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgRcLcLiteratorgR),0,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR));
   G__setnewtype(-1,NULL,0);
   G__search_typename2("vector<TVirtualArray*>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR),0,-1);
   G__setnewtype(-1,NULL,0);
   G__search_typename2("reverse_iterator<const_iterator>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgRcLcLiteratorgR),0,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR));
   G__setnewtype(-1,NULL,0);
   G__search_typename2("reverse_iterator<iterator>",117,G__get_linked_tagnum(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgRcLcLiteratorgR),0,G__get_linked_tagnum(&G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR));
   G__setnewtype(-1,NULL,0);
}

/*********************************************************
* Data Member information setup/
*********************************************************/

   /* Setting up class,struct,union tag member variable */

   /* cfd::CFDFire */
static void G__setup_memvarcfdcLcLCFDFire(void) {
   G__tag_memvar_setup(G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire));
   { cfd::CFDFire *p; p=(cfd::CFDFire*)0x1000; if (p) { }
   G__memvar_setup((void*)((long)(&p->tfire)-(long)(p)),105,0,0,-1,-1,-1,1,"tfire=",0,(char*)NULL);
   G__memvar_setup((void*)((long)(&p->maxamp)-(long)(p)),105,0,0,-1,-1,-1,1,"maxamp=",0,(char*)NULL);
   G__memvar_setup((void*)((long)(&p->tmax)-(long)(p)),105,0,0,-1,-1,-1,1,"tmax=",0,(char*)NULL);
   G__memvar_setup((void*)((long)(&p->maxdiff)-(long)(p)),105,0,0,-1,-1,-1,1,"maxdiff=",0,(char*)NULL);
   G__memvar_setup((void*)0,85,0,0,G__get_linked_tagnum(&G__dictcfdiscdataLN_TClass),G__defined_typename("atomic_TClass_ptr"),-2,4,"fgIsA=",0,(char*)NULL);
   }
   G__tag_memvar_reset();
}

extern "C" void G__cpp_setup_memvardictcfdiscdata() {
}
/***********************************************************
************************************************************
************************************************************
************************************************************
************************************************************
************************************************************
************************************************************
***********************************************************/

/*********************************************************
* Member function information setup for each class
*********************************************************/
static void G__setup_memfunccfdcLcLCFDFire(void) {
   /* cfd::CFDFire */
   G__tag_memfunc_setup(G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire));
   G__memfunc_setup("CFDFire",595,G__dictcfdiscdata_169_0_1, 105, G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire), -1, 0, 0, 1, 1, 0, "", (char*)NULL, (void*) NULL, 0);
   G__memfunc_setup("Class",502,G__dictcfdiscdata_169_0_2, 85, G__get_linked_tagnum(&G__dictcfdiscdataLN_TClass), -1, 0, 0, 3, 1, 0, "", (char*)NULL, (void*) G__func2void( (TClass* (*)())(&cfd::CFDFire::Class) ), 0);
   G__memfunc_setup("Class_Name",982,G__dictcfdiscdata_169_0_3, 67, -1, -1, 0, 0, 3, 1, 1, "", (char*)NULL, (void*) G__func2void( (const char* (*)())(&cfd::CFDFire::Class_Name) ), 0);
   G__memfunc_setup("Class_Version",1339,G__dictcfdiscdata_169_0_4, 115, -1, G__defined_typename("Version_t"), 0, 0, 3, 1, 0, "", (char*)NULL, (void*) G__func2void( (Version_t (*)())(&cfd::CFDFire::Class_Version) ), 0);
   G__memfunc_setup("Dictionary",1046,G__dictcfdiscdata_169_0_5, 121, -1, -1, 0, 0, 3, 1, 0, "", (char*)NULL, (void*) G__func2void( (void (*)())(&cfd::CFDFire::Dictionary) ), 0);
   G__memfunc_setup("IsA",253,(G__InterfaceMethod) NULL,85, G__get_linked_tagnum(&G__dictcfdiscdataLN_TClass), -1, 0, 0, 1, 1, 8, "", (char*)NULL, (void*) NULL, 1);
   G__memfunc_setup("ShowMembers",1132,(G__InterfaceMethod) NULL,121, -1, -1, 0, 1, 1, 1, 0, "u 'TMemberInspector' - 1 - -", (char*)NULL, (void*) NULL, 1);
   G__memfunc_setup("Streamer",835,(G__InterfaceMethod) NULL,121, -1, -1, 0, 1, 1, 1, 0, "u 'TBuffer' - 1 - -", (char*)NULL, (void*) NULL, 1);
   G__memfunc_setup("StreamerNVirtual",1656,G__dictcfdiscdata_169_0_9, 121, -1, -1, 0, 1, 1, 1, 0, "u 'TBuffer' - 1 - ClassDef_StreamerNVirtual_b", (char*)NULL, (void*) NULL, 0);
   G__memfunc_setup("DeclFileName",1145,G__dictcfdiscdata_169_0_10, 67, -1, -1, 0, 0, 3, 1, 1, "", (char*)NULL, (void*) G__func2void( (const char* (*)())(&cfd::CFDFire::DeclFileName) ), 0);
   G__memfunc_setup("ImplFileLine",1178,G__dictcfdiscdata_169_0_11, 105, -1, -1, 0, 0, 3, 1, 0, "", (char*)NULL, (void*) G__func2void( (int (*)())(&cfd::CFDFire::ImplFileLine) ), 0);
   G__memfunc_setup("ImplFileName",1171,G__dictcfdiscdata_169_0_12, 67, -1, -1, 0, 0, 3, 1, 1, "", (char*)NULL, (void*) G__func2void( (const char* (*)())(&cfd::CFDFire::ImplFileName) ), 0);
   G__memfunc_setup("DeclFileLine",1152,G__dictcfdiscdata_169_0_13, 105, -1, -1, 0, 0, 3, 1, 0, "", (char*)NULL, (void*) G__func2void( (int (*)())(&cfd::CFDFire::DeclFileLine) ), 0);
   // automatic copy constructor
   G__memfunc_setup("CFDFire", 595, G__dictcfdiscdata_169_0_14, (int) ('i'), G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire), -1, 0, 1, 1, 1, 0, "u 'cfd::CFDFire' - 11 - -", (char*) NULL, (void*) NULL, 0);
   // automatic destructor
   G__memfunc_setup("~CFDFire", 721, G__dictcfdiscdata_169_0_15, (int) ('y'), -1, -1, 0, 0, 1, 1, 0, "", (char*) NULL, (void*) NULL, 1);
   // automatic assignment operator
   G__memfunc_setup("operator=", 937, G__dictcfdiscdata_169_0_16, (int) ('u'), G__get_linked_tagnum(&G__dictcfdiscdataLN_cfdcLcLCFDFire), -1, 1, 1, 1, 1, 0, "u 'cfd::CFDFire' - 11 - -", (char*) NULL, (void*) NULL, 0);
   G__tag_memfunc_reset();
}


/*********************************************************
* Member function information setup
*********************************************************/
extern "C" void G__cpp_setup_memfuncdictcfdiscdata() {
}

/*********************************************************
* Global variable information setup for each class
*********************************************************/
static void G__cpp_setup_global0() {

   /* Setting up global variables */
   G__resetplocal();

}

static void G__cpp_setup_global1() {
}

static void G__cpp_setup_global2() {

   G__resetglobalenv();
}
extern "C" void G__cpp_setup_globaldictcfdiscdata() {
  G__cpp_setup_global0();
  G__cpp_setup_global1();
  G__cpp_setup_global2();
}

/*********************************************************
* Global function information setup for each class
*********************************************************/
static void G__cpp_setup_func0() {
   G__lastifuncposition();

}

static void G__cpp_setup_func1() {
}

static void G__cpp_setup_func2() {
}

static void G__cpp_setup_func3() {
}

static void G__cpp_setup_func4() {
}

static void G__cpp_setup_func5() {
}

static void G__cpp_setup_func6() {
}

static void G__cpp_setup_func7() {
}

static void G__cpp_setup_func8() {
}

static void G__cpp_setup_func9() {
}

static void G__cpp_setup_func10() {
}

static void G__cpp_setup_func11() {
}

static void G__cpp_setup_func12() {

   G__resetifuncposition();
}

extern "C" void G__cpp_setup_funcdictcfdiscdata() {
  G__cpp_setup_func0();
  G__cpp_setup_func1();
  G__cpp_setup_func2();
  G__cpp_setup_func3();
  G__cpp_setup_func4();
  G__cpp_setup_func5();
  G__cpp_setup_func6();
  G__cpp_setup_func7();
  G__cpp_setup_func8();
  G__cpp_setup_func9();
  G__cpp_setup_func10();
  G__cpp_setup_func11();
  G__cpp_setup_func12();
}

/*********************************************************
* Class,struct,union,enum tag information setup
*********************************************************/
/* Setup class/struct taginfo */
G__linked_taginfo G__dictcfdiscdataLN_TClass = { "TClass" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_TBuffer = { "TBuffer" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_TMemberInspector = { "TMemberInspector" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_TObject = { "TObject" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR = { "vector<ROOT::TSchemaHelper,allocator<ROOT::TSchemaHelper> >" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_reverse_iteratorlEvectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgRcLcLiteratorgR = { "reverse_iterator<vector<ROOT::TSchemaHelper,allocator<ROOT::TSchemaHelper> >::iterator>" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR = { "vector<TVirtualArray*,allocator<TVirtualArray*> >" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_reverse_iteratorlEvectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgRcLcLiteratorgR = { "reverse_iterator<vector<TVirtualArray*,allocator<TVirtualArray*> >::iterator>" , 99 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_cfd = { "cfd" , 110 , -1 };
G__linked_taginfo G__dictcfdiscdataLN_cfdcLcLCFDFire = { "cfd::CFDFire" , 99 , -1 };

/* Reset class/struct taginfo */
extern "C" void G__cpp_reset_tagtabledictcfdiscdata() {
  G__dictcfdiscdataLN_TClass.tagnum = -1 ;
  G__dictcfdiscdataLN_TBuffer.tagnum = -1 ;
  G__dictcfdiscdataLN_TMemberInspector.tagnum = -1 ;
  G__dictcfdiscdataLN_TObject.tagnum = -1 ;
  G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR.tagnum = -1 ;
  G__dictcfdiscdataLN_reverse_iteratorlEvectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgRcLcLiteratorgR.tagnum = -1 ;
  G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR.tagnum = -1 ;
  G__dictcfdiscdataLN_reverse_iteratorlEvectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgRcLcLiteratorgR.tagnum = -1 ;
  G__dictcfdiscdataLN_cfd.tagnum = -1 ;
  G__dictcfdiscdataLN_cfdcLcLCFDFire.tagnum = -1 ;
}


extern "C" void G__cpp_setup_tagtabledictcfdiscdata() {

   /* Setting up class,struct,union tag entry */
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_TClass);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_TBuffer);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_TMemberInspector);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_TObject);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_vectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgR);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlEROOTcLcLTSchemaHelpercOallocatorlEROOTcLcLTSchemaHelpergRsPgRcLcLiteratorgR);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_vectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgR);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_reverse_iteratorlEvectorlETVirtualArraymUcOallocatorlETVirtualArraymUgRsPgRcLcLiteratorgR);
   G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_cfd);
   G__tagtable_setup(G__get_linked_tagnum_fwd(&G__dictcfdiscdataLN_cfdcLcLCFDFire),sizeof(cfd::CFDFire),-1,29952,(char*)NULL,G__setup_memvarcfdcLcLCFDFire,G__setup_memfunccfdcLcLCFDFire);
}
extern "C" void G__cpp_setupdictcfdiscdata(void) {
  G__check_setup_version(30051515,"G__cpp_setupdictcfdiscdata()");
  G__set_cpp_environmentdictcfdiscdata();
  G__cpp_setup_tagtabledictcfdiscdata();

  G__cpp_setup_inheritancedictcfdiscdata();

  G__cpp_setup_typetabledictcfdiscdata();

  G__cpp_setup_memvardictcfdiscdata();

  G__cpp_setup_memfuncdictcfdiscdata();
  G__cpp_setup_globaldictcfdiscdata();
  G__cpp_setup_funcdictcfdiscdata();

   if(0==G__getsizep2memfunc()) G__get_sizep2memfuncdictcfdiscdata();
  return;
}
class G__cpp_setup_initdictcfdiscdata {
  public:
    G__cpp_setup_initdictcfdiscdata() { G__add_setup_func("dictcfdiscdata",(G__incsetup)(&G__cpp_setupdictcfdiscdata)); G__call_setup_funcs(); }
   ~G__cpp_setup_initdictcfdiscdata() { G__remove_setup_func("dictcfdiscdata"); }
};
G__cpp_setup_initdictcfdiscdata G__cpp_setup_initializerdictcfdiscdata;

