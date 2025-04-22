#!/bin/bash

mock_exam_dir=$(dirname "$(realpath "$0")")

python_script=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--single)
            python_script="$mock_exam_dir/mock_exam_single_support/mock_exam_single_support.py"
            shift
            ;;
        -m|--multiple)
            python_script="$mock_exam_dir/mock_exam_multiple_support/mock_exam_multiple_support.py"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-s|--single | -m|--multiple]"
            exit 1
            ;;
        *)
            echo "Error: Unknown option '$1'"
            echo "Usage: $0 [-s|--single | -m|--multiple]"
            exit 1
            ;;
    esac
done

if [[ -z "$python_script" ]]; then
    echo "Error: Please specify either -s/--single or -m/--multiple"
    echo "Usage: $0 [-s|--single | -m|--multiple]"
    exit 1
fi

"$mock_exam_dir/mock-venv/bin/python3" "$python_script"