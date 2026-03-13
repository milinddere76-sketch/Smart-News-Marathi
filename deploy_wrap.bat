@echo off
powershell.exe -ExecutionPolicy Bypass -File .\master_deploy.ps1 > fly_deployment.log 2>&1
