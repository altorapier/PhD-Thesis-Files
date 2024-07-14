// This script sets a Bentham monochromator to a spcific filter passed by command line argument

#include <windows.h>
#include <iostream>
#include <stdio.h>
#include <conio.h>
#include <time.h>
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\dllerror.h"
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\dlltoken.h"
#include "C:\Users\e47018kr\Documents\BenthamMonoSweep\c_libs\bendll.h"

int main(int argc, char** argv) {

  char system_cfg[100], system_atr[100], error[100] ;
  int result = BI_OK;

  // --------------------------------------------------
  // Parse command line switches

  double filterPos = atoi(argv[1]);

  // --------------------------------------------------
  // Build the system model, load the system's setup and initialise

  init();

  strcpy(system_cfg,"C:\\Program Files (x86)\\Bentham\\SDK\\Configuration Files\\System-35838.cfg");
  strcpy(system_atr,"C:\\Program Files (x86)\\Bentham\\SDK\\Configuration Files\\System-35838.atr");
  //strcpy(system_cfg,"C:\\Users\\ATLab2\\Desktop\\BenthamMonoSweep\\config\\mono1.cfg");
  //strcpy(system_atr,"C:\\Users\\ATLab2\\Desktop\\BenthamMonoSweep\\config\\mono1.atr");

  result = BI_build_system_model(system_cfg,error);
  result = BI_load_setup(system_atr);
  result = BI_initialise();

  if (result != BI_OK ) std::cerr << "Error during initialisation" << std::endl;

  // --------------------------------------------------
  // Get and set mirror position

  char id;
  double value = 0;

  strcpy(&id, "fwheel");

  // Get position

  /*result = BI_set(&id, SAMSwitchWL, 0, 0);
  result = BI_get(&id, SAMSwitchWL, 0, &value);
  std::cout << "Got value: " << value << std::endl;

  if (result != BI_OK ) std::cerr  << "BI_get failed" << std::endl ; */

  // Set position

  result = BI_set(&id, FWheelCurrentPosition, 0, filterPos);

  if (result != BI_OK ) std::cerr  << "BI_set failed" << std::endl ;

  return 0;
}
