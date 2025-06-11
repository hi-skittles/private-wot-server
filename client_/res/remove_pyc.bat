@echo off
REM ----------------------------------------------------------------
REM .pyc is dirty and nasty!! we don't want any of them in our folders,, begone!!!
REM ----------------------------------------------------------------

REM Change to the directory where this script resides (optional)
cd /d "%~dp0"

REM “del /S” will recurse; “/Q” suppresses confirmation prompts
for /R "%~dp0" %%f in (*.pyc) do (
    echo Deleting "%%f"
    del /F /Q "%%f"
)


REM Exit with the same code as the delete command
exit /b %ERRORLEVEL%
