#!/bin/bash
while true; do
  python main.py
  if [ $? -eq 5 ]; then
    echo "Oanda server is down, will retry in one hour"
    sleep 3600
  fi
  echo "Will restart oandabot in five seconds, press Ctrl+C to exit"
  sleep 5
  echo "Restarting"
done


