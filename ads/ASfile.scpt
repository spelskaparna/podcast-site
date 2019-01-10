on run argv
    set SomeName to (POSIX file (item 1 of argv))
    tell application "Adobe After Effects CC 2019"
        DoScriptFile SomeName
        DoScript item 2 of argv
   end tell
end run
