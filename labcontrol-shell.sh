#!/usr/bin/env bash
# Labcontrol interactive shell launcher
# Prints banner via bash venv, then drops into fish with venv active
cd /home/tom/Desktop/labcontrol
source .venv/bin/activate
python -c "from labcontrol.banner import print_banner; print_banner()"
echo ""
exec fish -C "source /home/tom/Desktop/labcontrol/.venv/bin/activate.fish"
