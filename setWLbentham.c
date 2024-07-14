// This script sets a Bentham monochromator to a wavelength passed by command line argument

#include <windows.h>
#include <iostream>
#include <stdio.h>
#include <conio.h>
#include <time.h>
#include <sstream>
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\dllerror.h"
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\dlltoken.h"
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\bendll.h"

int main(int argc, char** argv) {

  char system_cfg[100], system_atr[100], error[100] ;
  int result = BI_OK;

  // --------------------------------------------------
  // Parse command line switches

  float wavelength = atof(argv[1]);
  long delay = atoi(argv[2]);
  bool park;// = atoi(argv[2]);;
  std::stringstream(argv[3]) >> park;

  // --------------------------------------------------
  // Build the system model, load the system's setup and initialise

  init();

  strcpy(system_cfg,"C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\System-35838.cfg");
  strcpy(system_atr,"C:\\Users\\e47018kr\\Documents\\BenthamMonoSweep\\c_codes\\System-35838.atr");
  //strcpy(system_cfg,"E:\\Bentham\\SDK\\Configuration Files\\Replacement files\\mono1.cfg");
  //strcpy(system_atr,"E:\\Bentham\\SDK\\Configuration Files\\Replacement files\\mono1.atr");

  result = BI_build_system_model(system_cfg,error);
  result = BI_load_setup(system_atr);
  result = BI_initialise();

  if ( park ) result = BI_park();

  if (result != BI_OK ) std::cerr << " Error running BI_initialise " << std::endl ;

  // --------------------------------------------------
  // Move to specified wavelength

  result = BI_select_wavelength(wavelength, &delay);

  if (result != BI_OK ) std::cerr  << "BI_select_wavelength : Failed" << std::endl ;

  return 0;
}
