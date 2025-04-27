#!/bin/bash

mock_exam_dir=$(dirname "$(realpath "$0")")

if [[ -z "$python_script" ]]; then
    echo "Error: Please specify either -b/--build or -s/--start or -h/--help"
    echo "Usage: $0 [-b|--build | -s|--start | -h|--help]"
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        -b|--build)
            "$mock_exam_dir/mock-venv/bin/pip" "install" "."
            exit 1
            ;;
        -s|--start)
            "$mock_exam_dir/mock-venv/bin/python3" "-m" "mock_exam_simulator"
            exit 1
            ;;
        -h|--help)
            echo "Usage: $0 [-b|--build | -s|--start | -h|--help]"
            exit 1
            ;;
        *)
            echo "Error: Unknown option '$1'"
            echo "Usage: $0 [-b|--build | -s|--start | -h|--help]"
            exit 1
            ;;
    esac
done
