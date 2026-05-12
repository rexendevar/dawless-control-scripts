#!/bin/bash
sudo modprobe -r fb_ili9340   # unload (use whatever name lsmod showed)
sudo modprobe fb_ili9340      # reload