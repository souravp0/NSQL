#!/bin/bash

check_process_running() {
    local port="$1"
    local process_count=$(netstat -tln | grep ":$port " | wc -l)

    if [ "$process_count" -gt 0 ]; then
        return 0
    else
        return 1
    fi
}

start_process() {
    python3 ~/NSQL/application.py &
    # Replace '/path/to/your_script.py' with the actual path to your Python script
}

target_port=5003

if check_process_running "$target_port"; then
    echo "Process on port $target_port is already running."
else
    echo "Starting process on port $target_port..."
    start_process
fi