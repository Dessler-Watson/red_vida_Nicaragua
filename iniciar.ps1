$runtime = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Set-Location -LiteralPath $PSScriptRoot
if (Test-Path -LiteralPath $runtime) { & $runtime servidor.py --port 8080 } else { python servidor.py --port 8080 }
