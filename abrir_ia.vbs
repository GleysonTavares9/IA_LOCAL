Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
batchFile = fso.BuildPath(strPath, "INICIAR_IA.bat")
WshShell.CurrentDirectory = strPath
WshShell.Run chr(34) & batchFile & chr(34), 1
Set WshShell = Nothing
Set fso = Nothing