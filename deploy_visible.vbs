Set objShell = CreateObject("WScript.Shell")
Dim sPath : sPath = "d:\Apps\Smart News Marathi"
Dim sFly  : sFly  = "C:\Users\Priyansh Dere\.fly\bin\flyctl.exe"

' Open a new visible CMD window and run all 3 deploys sequentially
objShell.Run "cmd.exe /k """ & _
  "echo =========== DEPLOYING BACKEND =========== && " & _
  "cd /d """ & sPath & "\backend"" && " & _
  """" & sFly & """ deploy --remote-only && " & _
  "echo =========== DEPLOYING FRONTEND =========== && " & _
  "cd /d """ & sPath & "\frontend"" && " & _
  """" & sFly & """ deploy --remote-only && " & _
  "echo =========== DEPLOYING STREAM ENGINE =========== && " & _
  "cd /d """ & sPath & "\stream-engine"" && " & _
  """" & sFly & """ deploy --remote-only && " & _
  "echo =========== ALL DONE! ===========""", 1, False
