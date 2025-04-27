#!/bin/bash

mock_exam_dir=$(dirname "$(realpath "$0")")

"$mock_exam_dir/mock-venv/bin/pip" "install" "."

"$mock_exam_dir/mock-venv/bin/python3" "-m" "mock_exam_simulator"