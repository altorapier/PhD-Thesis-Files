// This script sets a Bentham monochromator to a specific grating passed by command line argument

#include <windows.h>
#include <iostream>
#include <stdio.h>
#include <conio.h>
#include <time.h>
#include "E:\Bentham\SDK\lang\c\dllerror.h"
#include "E:\Bentham\SDK\lang\c\dlltoken.h"
#include "E:\Bentham\SDK\lang\c\bendll.h"

int main(int argc, char** argv) {

  char system_cfg[100], system_atr[100], error[100] ;
  int result = BI_OK;

  // --------------------------------------------------
  // Parse command line switches

  double selectedGrating = atoi(argv[1]);

  // --------------------------------------------------
  // Build the system model, load the system's setup and initialise

  init();

  //strcpy(system_cfg,"E:\\Bentham\\SDK\\Configuration Files\\system-23427.cfg");
  //strcpy(system_atr,"E:\\Bentham\\SDK\\Configuration Files\\system-23427.atr");
  strcpy(system_cfg,"E:\\Bentham\\SDK\\Configuration Files\\Replacement files\\monoOli1.cfg");
  strcpy(system_atr,"E:\\Bentham\\SDK\\Configuration Files\\Replacement files\\monoOli1.atr");

  result = BI_build_system_model(system_cfg,error);
  result = BI_load_setup(system_atr);
  result = BI_initialise();

  if (result != BI_OK ) std::cerr << "Error during initialisation" << std::endl;

  // --------------------------------------------------
  // Get and set mirror position

  char id;
  double value = 0;

  strcpy(&id, "exit1");

  result = BI_park();

  /*
  // Get position

  //result = BI_set(&id, SAMSwitchWL, 0, 0);
  result = BI_get(&id, MonochromatorCurrentGrating, 0, &value);
  std::cout << "Got value: " << value << std::endl;

  if (result != BI_OK ) std::cerr  << "BI_get failed" << std::endl ;

  // Set position

  result = BI_set(&id, MonochromatorCurrentGrating, 0, selectedGrating);

  if (result != BI_OK ) std::cerr  << "BI_set failed" << std::endl ;
    */
  return 0;
}
