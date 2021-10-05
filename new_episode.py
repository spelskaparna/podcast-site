import os, sys
import subprocess


path = "content/episode"
dirs = os.listdir(path)

numbers = []
for file in dirs:
    index = file.find(".md")
    if index > -1:
        number = file[:index]
        numbers.append(int(number))
numbers.sort()
next_number = numbers[-1] + 1

subprocess.run(["hugo", "new", f"episode/{next_number}.md"])

