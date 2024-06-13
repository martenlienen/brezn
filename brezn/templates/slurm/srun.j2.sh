#!/bin/bash

# Change into job directory
cd "${0%/*}"

# Run command
srun --pty {% for key, value in srun_options.items() %}{{("--" ~ key ~ "=" ~ value) | quote}} {% endfor %}{{("./" ~ command_script) | quote}}
