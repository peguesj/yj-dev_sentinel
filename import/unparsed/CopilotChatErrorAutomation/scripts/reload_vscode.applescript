tell application "Visual Studio Code"
    activate
    delay 1
    tell application "System Events"
        keystroke "p" using {command down, shift down}
        delay 0.5
        keystroke "Developer: Reload Window"
        delay 0.5
        keystroke return
    end tell
end tell
