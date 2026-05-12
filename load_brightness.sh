#!/bin/bash
cd "$(dirname "$0")"

gpio -g mode 18 pwm;
gpio pwmc 1000;
gpio -g pwm 18 $(cat ./brightness.txt)