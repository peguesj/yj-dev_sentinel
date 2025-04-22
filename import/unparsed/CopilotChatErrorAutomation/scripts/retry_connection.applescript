tell application "Visual Studio Code"
    activate
    delay 1
    tell application "System Events"
        -- simulate Retry
        keystroke "r" using {command down}
    end tell
end tell
