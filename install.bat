@echo off
setlocal

set "COMMANDS_DIR=%USERPROFILE%\.claude\commands"
set "SOURCE=%~dp0upgrade-analyzer.md"

echo Installing upgrade-analyzer...

if not exist "%SOURCE%" (
    echo Error: upgrade-analyzer.md not found: "%SOURCE%"
    exit /b 1
)

if not exist "%COMMANDS_DIR%" (
    mkdir "%COMMANDS_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create directory: "%COMMANDS_DIR%"
        exit /b 1
    )
)

copy /Y "%SOURCE%" "%COMMANDS_DIR%\upgrade-analyzer.md" >nul
if errorlevel 1 (
    echo Error: Failed to copy upgrade-analyzer.md
    exit /b 1
)

echo Installation complete.
echo Start Claude Code and use the /upgrade-analyzer command.

endlocal
exit /b 0
