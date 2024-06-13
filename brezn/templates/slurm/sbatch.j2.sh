#!/bin/bash
{%- for key, value in sbatch_options.items() %}
#SBATCH {{("--" ~ key ~ "=" ~ value) | quote}}
{%- endfor %}

# Change into job directory
cd "${0%/*}"

# Run command
srun {{("./" ~ command_script) | quote}}
