!include nsDialogs.nsh
!include LogicLib.nsh
!macro _FileExists2 _a _b _t _f
	StrCmp `${_b}` `` `${_f}` 0
	IfFileExists `${_b}` `0` `${_f}` ;returns true if this is a directory
	IfFileExists `${_b}\*.*` `${_f}` `${_t}` ;so if it is a directory, jump to false
!macroend
!undef FileExists
!define FileExists `"" FileExists2`
!macro _DirExists _a _b _t _f
	StrCmp `${_b}` `` `${_f}` 0
	IfFileExists `${_b}\*.*` `${_t}` `${_f}`
!macroend
!define DirExists `"" DirExists`
!include mui2.nsh
!include WinMessages.nsh

Var PythonList
Var Directory
Var Browse
Var PythonPath
Var PythonVer
!macro PAGE_PYTHON_MODULE 
Page custom PythonModulePage PythonModulePage_OnLeave
!macroend

Function PythonModulePage
	!insertmacro MUI_HEADER_TEXT_PAGE "Install Python Module" "Please select where to install the Python module"
    nsDialogs::Create 1018
	Pop $0

	${NSD_CreateListBox} 0 0 300u 120u ""
	Pop $PythonList

    StrCpy $0 0
    EnumRegKey $1 HKLM SOFTWARE\Python\PythonCore $0
    ${DoWhile} $1 != ""
        ReadRegStr $2 HKLM SOFTWARE\Python\PythonCore\$1\InstallPath ""
        ${if} $2 != "" 
            ${NSD_LB_AddString} $PythonList "$1" 
        ${endif}
        IntOp $0 $0 + 1
        EnumRegKey $1 HKLM SOFTWARE\Python\PythonCore $0
    ${Loop}
    ${NSD_LB_GetCount} $PythonList $0
    ${if} $0 == 0
    MessageBox MB_ICONINFORMATION|MB_OK "No Python version detected. If you don't have Python installed you should install it first. Otherwise you can input the python directory below."
    ${endif}
    ${NSD_LB_AddString} $PythonList "Custom"
    ${NSD_LB_SelectString} $PythonList $PythonVer
    ${NSD_OnChange} $PythonList PythonModulePage_OnLeave_OnChange_PythonList
    
	${NSD_CreateDirRequest} 0 121u 280u 15u ""
	Pop $Directory  
    
    ${NSD_CreateButton} 281u 121u 19u 15u "..."
    Pop $Browse
    GetFunctionAddress $0 PythonModulePage_OnClick_Browse
    
    
    nsDialogs::OnClick /NOUNLOAD $Browse $0    
    
    nsDialogs::Show
FunctionEnd

Function PythonModulePage_OnLeave
${NSD_GetText} $Directory $PythonPath
${NSD_LB_GetSelection} $PythonList $PythonVer
${If} $PythonPath == ""
${OrIfNot} ${DirExists} $PythonPath 
    Abort
${endif}
FunctionEnd

Function PythonModulePage_OnLeave_OnChange_PythonList
${NSD_LB_GetSelection} $PythonList $0
${if} $0 != "Custom"
    EnableWindow $Directory 0
    EnableWindow $Browse 0
    ${if} $0 != ""
        ReadRegStr $1 HKLM SOFTWARE\Python\PythonCore\$0\InstallPath ""
        ${NSD_SetText} $Directory $1
    ${endif}
${else}
    EnableWindow $Directory 1
    EnableWindow $Browse 1
${endif}

FunctionEnd

Function PythonModulePage_OnClick_Browse
    
    ${NSD_GetText} $Directory $0

	nsDialogs::SelectFolderDialog /NOUNLOAD "Please select a target directory" "$0"

	Pop $0
	${If} $0 == error

		Abort

	${EndIf}

	${NSD_SetText} $Directory $0

FunctionEnd