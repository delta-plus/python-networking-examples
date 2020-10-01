#!/bin/bash

pkill chatClient.py
pkill chatServer.py
rm -f *mp3
rm -f ./files/*
i3-msg -q workspace 2
xdotool type "./chatServer.py"
xdotool key Return
i3-msg -q workspace 3
xdotool type "../python/chatClient.py 127.0.0.1 5000"
xdotool key Return
xdotool type "../python/chatClient.py 127.0.0.1 5000"
xdotool key Return
sleep .5
xdotool type "\nick one"
xdotool key Return
sleep .5
xdotool type "\e food"
xdotool key Return
sleep .5
xdotool key alt+Down
sleep .5
xdotool type "../python/chatClient.py 127.0.0.1 5000 2>/dev/null"
xdotool key Return
xdotool type "../python/chatClient.py 127.0.0.1 5000 2>/dev/null"
xdotool key Return
sleep .5
xdotool type "\nick two"
xdotool key Return
sleep .5
xdotool type "\e food"
xdotool key Return
sleep .5
xdotool key alt+Up
sleep .5
xdotool type "\f two Classical-guitar-music.mp3"
xdotool key Return
sleep .5
xdotool key alt+Down
sleep .5
xdotool type "\f y"
xdotool key Return
sleep 1
xdotool type "\x"
xdotool key Return
sleep .5
xdotool type "diff *mp3 ../python/*mp3"
xdotool key Return
xdotool key alt+Up
sleep 1
i3-msg -q workspace 4
xdotool type "./res"
sleep 1
xdotool key Return
