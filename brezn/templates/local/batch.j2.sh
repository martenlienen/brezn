#!/bin/bash

# Change into job directory
cd "${0%/*}"

# Run command and record both stdout and stderr transparently
{{("./" ~ command_script) | quote}} > >(tee ./stdout.log) 2> >(tee ./stderr.log >&2)
