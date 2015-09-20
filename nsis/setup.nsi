###############################################################
#NSIS script for PARPG
#
# Non standard plugins
#
# ZipDLL : http://nsis.sourceforge.net/ZipDLL_plug-in
# Please note the install instructions
#
# Advanced Uninstall Log 2
# Header for that is in the same directory as this script - AdvUninstLog2.nsh
#
# Python module installer
# Header for that is in the same directory as this script - python-module.nsh
#
!define PRODUCT_NAME "PARPG Techdemo 2"
!define PRODUCT_VERSION "SVN trunk r788"
!define PRODUCT_PUBLISHER "PARPG Development Team"
!define PRODUCT_WEB_SITE "http://www.parpg.net/"
!define INSTDIR_REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define INSTDIR_REG_ROOT "HKLM"

!define PARPG_DIR "game"
!define EXEC_SCRIPT_NAME "parpg-run.py"
# MUI 1.67 compatible ------
!include "MUI2.nsh"
!include "AdvUninstLog2.nsh"
!include "python-module.nsh"
!include "download_mirror.nsh"

# MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${PARPG_DIR}\gui\icons\window_icon.ico"
!define MUI_UNICON "${PARPG_DIR}\gui\icons\window_icon.ico"

# Welcome page
!insertmacro MUI_PAGE_WELCOME
!define MUI_PAGE_CUSTOMFUNCTION_PRE SelectFilesCheck
!insertmacro MUI_PAGE_COMPONENTS

# License page
!insertmacro MUI_PAGE_LICENSE "${PARPG_DIR}\license\gpl30.license"
# Instfiles page Externals
!define MUI_PAGE_CUSTOMFUNCTION_PRE SelectFilesExternals
!insertmacro MUI_PAGE_INSTFILES
# Directory page PARPG
!define MUI_PAGE_CUSTOMFUNCTION_PRE SelectFilesPARPG
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro PAGE_PYTHON_MODULE
# Instfiles page PARPG
!insertmacro MUI_PAGE_INSTFILES


# Finish page
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE DeleteSectionsINI
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

# Language files
!insertmacro MUI_LANGUAGE "English"

# ZipFile Support
!include "ZipDLL.nsh"

# MUI end ------

RequestExecutionLevel admin #For Vista. Admin is needed to install in program files directory

Name "${PRODUCT_NAME}"
OutFile "parpg_td2_r877_win32.exe"
InstallDir "$PROGRAMFILES\PARPG"
ShowInstDetails show
ShowUnInstDetails show

!insertmacro UNATTENDED_UNINSTALL

#Externals, at least Python, have to be installed first
SectionGroup Externals Externals
#---------- DOWNLOAD PYTHON -------
Section "ActivePython (required)" Python
  DetailPrint "Downloading Python"
  NSISdl::download http://downloads.activestate.com/ActivePython/releases/2.7.1.4/ActivePython-2.7.1.4-win32-x86.msi $TEMP\pysetup.msi
  Pop $R0 #Get the return value
    StrCmp $R0 "success" +3
      MessageBox MB_OK "Failed to download Python installer: $R0"
      Quit

  DetailPrint "Installing Python"
  ExecWait '"msiexec" /i "$TEMP\pysetup.msi"'

  DetailPrint "Deleting Python installer"
  Delete $TEMP\pysetup.msi
SectionEnd

#------------ PyYAML --------------
Section "PyYAML (required)" PyYAML
  DetailPrint "Downloading PyYAML"
  NSISdl::download http://pyyaml.org/download/pyyaml/PyYAML-3.09.win32-py2.7.exe $TEMP\pyaml_setup.exe
  Pop $R0 #Get the return value
    StrCmp $R0 "success" +3
      MessageBox MB_OK "Failed to download PyYAML installer: $R0"
      Quit

  DetailPrint "Installing PyYAML"
  ExecWait "$TEMP\pyaml_setup.exe"

  DetailPrint "Deleting PyYAML installer"
  Delete "$TEMP\PyYAML_setup.exe"
SectionEnd

#----------- OPEN AL --------------
Section "OpenAL (required)" OpenAL
  SetDetailsPrint textonly
  NSISdl::download http://connect.creativelabs.com/openal/Downloads/oalinst.zip $TEMP\oalinst.zip
  
  DetailPrint "Extracting OpenAL archive"
  !insertmacro ZIPDLL_EXTRACT $TEMP\oalinst.zip $TEMP oalinst.exe

  DetailPrint "Installing OpenAL"
  ExecWait "$TEMP\oalinst.exe"

  DetailPrint "Deleting OpenAL installer"
  Delete "$TEMP\oalinst.exe"
  Delete "$TEMP\oalinst.zip"
SectionEnd

Section "FIFE (required)" FIFE
    DetailPrint "Downloading FIFE installer"
	Push "http://puzzle.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://mesh.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://aarnet.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://cdnetworks-us-1.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://ovh.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://ignum.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://tenet.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://jaist.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://garr.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push "http://cdnetworks-kr-2.dl.sourceforge.net/project/fife/active/packages/FIFE-0.3.2r2_installer_win32.exe"
	Push 10
	Push "$TEMP\FIFE-0.3.2r2_installer_win32.exe"
	Call DownloadFromRandomMirror
	Pop $0
    
	StrCmp $0 "cancel" 0 +3
		MessageBox MB_OK "Download canceled"
		Goto End
	StrCmp $0 "success" 0 +3
        DetailPrint "Installing FIFE"
		ExecWait "$TEMP\FIFE-0.3.2r2_installer_win32.exe"
        Goto End
	MessageBox MB_OK "Error $0"
	End:
    DetailPrint "Deleting FIFE Installer"
    Delete "$TEMP\FIFE-0.3.2r2_installer_win32.exe"
SectionEnd

#--------- SECTION END ------------
SectionGroupEnd

SectionGroup PARPG PARPG
Section "PARPG Module" PARPG-module
  SectionIn RO
  DetailPrint "Installing PARPG python package"
  SetOutPath "$PythonPath\lib\site-packages"
  SetOverwrite try
  FILE /r /x *svn* "${PARPG_DIR}\parpg" 
  SetAutoClose true
SectionEnd
#------------ Main. Packages PARPG code --------------
Section "PARPG Datafiles" PARPG-data
  SectionIn RO
  SetOverwrite try
  
  # get all the core PARPG files
  SetOutPath "$INSTDIR\dialogue"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\dialogue\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\fonts"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\fonts\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\gui"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\gui\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\maps"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\maps\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\music"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\music\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\objects"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\objects\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\quests"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\quests\" 
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\character_scripts"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\character_scripts\"
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetOutPath "$INSTDIR\license"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE /r /x *svn* "${PARPG_DIR}\license\"
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL

  SetOutPath "$INSTDIR"
  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
  FILE "${PARPG_DIR}\README"
  FILE "${PARPG_DIR}\AUTHORS"
  FILE "${PARPG_DIR}\run.py" 
  FILE "${PARPG_DIR}\system.cfg"
  
  RENAME "README" "README.txt"
  RENAME "AUTHORS" "AUTHORS.txt"
  RENAME "run.py" "${EXEC_SCRIPT_NAME}"

  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL
  SetAutoClose true
SectionEnd
# Tools not included as they aren't ready for distribution
#Section -Tools
  #SetOutPath "$INSTDIR\tools\map_editor"
  #SetOverwrite try
#SectionEnd

Section "-Additional" -AdditionalIcons
  SectionIn RO
  #avoid shortcuts headaches on vista by doing everything in the all users start menu
  SetShellVarContext all
  SetOutPath $INSTDIR
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortcut '$SMPROGRAMS\${PRODUCT_NAME}\uninstall.lnk' '${UNINST_EXE}'
  SetOutPath "$INSTDIR" #this makes the following shortcut run in the installed directory
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\PARPG.lnk" "$INSTDIR\${EXEC_SCRIPT_NAME}"
SectionEnd

Section "-Post" -Post
  SectionIn RO
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "UninstallString" "${UNINST_EXE}"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayIcon" "$INSTDIR\gui\icons\window_icon.ico"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd
SectionGroupEnd

##===========================================================================
## Settings
##===========================================================================
 
!define PARPG_StartIndex ${PARPG}
!define PARPG_EndIndex   ${-Post}
 
!define EXT_StartIndex ${Externals}
!define EXT_EndIndex   ${Fife}

Function .OnInit
  !insertmacro UNINSTALL.LOG_PREPARE_INSTALL
  !insertmacro SetSectionFlag ${PARPG} ${SF_RO}
  StrCpy $PythonPath ""
  StrCpy $PythonVer "Custom"
  InitPluginsDir
FunctionEnd

## If user goes back to this page from 1st Directory page
## we need to put the sections back to how they were before
Var IfBack
Function SelectFilesCheck
 StrCmp $IfBack 1 0 NoCheck
  Call ResetFiles
 NoCheck:
FunctionEnd

Function IsExternalsSelected
Push $R0
Push $R1
 
 StrCpy $R0 ${EXT_StartIndex}    # Group 2 start
 
  Loop:
   IntOp $R0 $R0 + 1
   SectionGetFlags $R0 $R1			# Get section flags
    IntOp $R1 $R1 & ${SF_SELECTED}
    StrCmp $R1 ${SF_SELECTED} 0 +3		# If section is selected, done
     StrCpy $R0 1
     Goto Done
    StrCmp $R0 ${EXT_EndIndex} 0 Loop
 
 Done:
Pop $R1
Exch $R0
FunctionEnd

## Here we are selecting first sections to install
## by unselecting all the others!
Function SelectFilesExternals
 
 # If user clicks Back now, we will know to reselect Group 2's sections for
 # Components page
 StrCpy $IfBack 1
 
 # We need to save the state of the Group 2 Sections
 # for the next InstFiles page
Push $R0
Push $R1
 
 StrCpy $R0 ${PARPG_StartIndex} # Group 2 start
 
  Loop:
   IntOp $R0 $R0 + 1
   SectionGetFlags $R0 $R1				    # Get section flags
    WriteINIStr "$PLUGINSDIR\sections.ini" Sections $R0 $R1 # Save state
    !insertmacro UnselectSection $R0			    # Then unselect it
    StrCmp $R0 ${PARPG_EndIndex} 0 Loop
 
 # Don't install prog 1?
 Call IsExternalsSelected
 Pop $R0
 StrCmp $R0 1 +4
  Pop $R1
  Pop $R0
  Abort
 
Pop $R1
Pop $R0
FunctionEnd

## Here we need to unselect all Group 1 sections
## and then re-select those in Group 2 (that the user had selected on
## Components page)
Function SelectFilesPARPG
Push $R0
Push $R1
 
 StrCpy $R0 ${EXT_StartIndex}    # Group 1 start
 
  Loop:
   IntOp $R0 $R0 + 1
    !insertmacro UnselectSection $R0		# Unselect it
    StrCmp $R0 ${EXT_EndIndex} 0 Loop
 
 Call ResetFiles
 
Pop $R1
Pop $R0
FunctionEnd

## This will set all sections to how they were on the components page
## originally
Function ResetFiles
Push $R0
Push $R1
 
 StrCpy $R0 ${PARPG_StartIndex}    # Group 2 start
 
  Loop:
   IntOp $R0 $R0 + 1
   ReadINIStr "$R1" "$PLUGINSDIR\sections.ini" Sections $R0 # Get sec flags
    SectionSetFlags $R0 $R1				  # Re-set flags for this sec
    StrCmp $R0 ${PARPG_EndIndex} 0 Loop
 
Pop $R1
Pop $R0
FunctionEnd

## Here we are deleting the temp INI file at the end of installation
Function DeleteSectionsINI
 FlushINI "$PLUGINSDIR\Sections.ini"
 Delete "$PLUGINSDIR\Sections.ini"
FunctionEnd

Function .onInstSuccess
  !insertmacro UNINSTALL.LOG_UPDATE_INSTALL
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  #avoid shortcuts headaches on vista by doing everything in the all users start menu
  SetShellVarContext all
  
  # remove data files
  !insertmacro UNINSTALL.NEW_UNINSTALL "$INSTDIR"
  
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\PARPG.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\uninstall.lnk"
  RmDir "$SMPROGRAMS\${PRODUCT_NAME}"
  
  Delete "$INSTDIR\*.log"
  Delete "$INSTDIR\system.cfg"
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  
  RMDir "$INSTDIR"

  # Remove shortcuts
  RMDir /r "$SMPROGRAMS\PARPG"
 
  # Remove Registry keys
  DeleteRegKey ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}"
  SetAutoClose true
SectionEnd


LangString DESC_PARPG ${LANG_ENGLISH} "PARPG - Techdemo 1 SVN r788"
LangString DESC_Python ${LANG_ENGLISH} "ActivePython 2.6.4.8 - Required to run PARPG. Requires an active internet connection to install."
LangString DESC_FIFE ${LANG_ENGLISH} "FIFE-0.3.2r2 - Required to run PARPG."
LangString DESC_PyYAML ${LANG_ENGLISH} "PyYAML 3.09 - Required Python Module. Requires an active internet connection to install."
LangString DESC_OpenAL ${LANG_ENGLISH} "OpenAL - Required for sound effects and music playback."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${PARPG} $(DESC_PARPG)
  !insertmacro MUI_DESCRIPTION_TEXT ${Python} $(DESC_Python)
  !insertmacro MUI_DESCRIPTION_TEXT ${FIFE} $(DESC_FIFE)
  !insertmacro MUI_DESCRIPTION_TEXT ${PyYAML} $(DESC_PyYAML)
  !insertmacro MUI_DESCRIPTION_TEXT ${OpenAL} $(DESC_OpenAL)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
