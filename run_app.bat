@echo off
setlocal

:: Get the directory of the batch file
set "mock_exam_dir=%~dp0"

:: Remove trailing backslash if present
set "mock_exam_dir=%mock_exam_dir:~0,-1%"

echo %mock_exam_dir%
cd %mock_exam_dir%

call pip install .

call python3 -m "mock_exam_simulator"

endlocal