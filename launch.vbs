' ─────────────────────────────────────────────────────────────
'  PixelPeel — Silent Launcher
'  This is what your Desktop/Start Menu shortcut points to.
'  It sets environment variables and starts the app with no
'  console window visible.
' ─────────────────────────────────────────────────────────────
Dim oShell, oFSO, appDir

Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

' Resolve the folder where this .vbs file lives
appDir = oFSO.GetParentFolderName(WScript.ScriptFullName)

' Disable numba JIT — prevents pymatting from hanging on import.
' rembg uses ONNX Runtime for removal; this only affects optional
' alpha-matting refinement and has no impact on quality.
oShell.Environment("Process")("NUMBA_DISABLE_JIT") = "1"

' Run pythonw (no console window), non-blocking
' pythonw is the same as python but suppresses the black CMD window
oShell.Run "pythonw """ & appDir & "\main.py""", 0, False
