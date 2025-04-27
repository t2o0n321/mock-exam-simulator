@echo off
setlocal enabledelayedexpansion

:: Get the directory of the batch file
set "mock_exam_dir=%~dp0"
set "mock_exam_dir=%mock_exam_dir:~0,-1%"

:: Check if argument is provided
if "%~1"=="" (
    echo Error: Please specify an option.
    echo Usage: %~nx0 [-b^|--build ^| -s^|--start ^| -h^|--help]
    goto :eof
)

:: Handle options
if /i "%~1"=="-b" (
    call pip install .
    goto :eof
) else if /i "%~1"=="--build" (
    call pip install .
    goto :eof
) else if /i "%~1"=="-s" (
    call python3 -m mock_exam_simulator
    goto :eof
) else if /i "%~1"=="--start" (
    call python3 -m mock_exam_simulator
    goto :eof
) else if /i "%~1"=="-h" (
    echo Usage: %~nx0 [-b^|--build ^| -s^|--start ^| -h^|--help]
    goto :eof
) else if /i "%~1"=="--help" (
    echo Usage: %~nx0 [-b^|--build ^| -s^|--start ^| -h^|--help]
    goto :eof
) else (
    echo Error: Unknown option '%~1'
    echo Usage: %~nx0 [-b^|--build ^| -s^|--start ^| -h^|--help]
    goto :eof
)

endlocal
