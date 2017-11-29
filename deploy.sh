#!/bin/bash

echo -e "\033[0;32mDeploying updates to GitHub...\033[0m"

# Build the project.
hugo -v --theme=rocktopus --buildFuture

# Go To Public folder
cd public

# Create a simple .gitignore to avoid unnecessary files
echo ".DS_Store" > .gitignore

# Add changes to git.
git add -A

# Commit changes.
msg="rebuilding site `date`"
if [ $# -eq 1 ]
  then msg="$1"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master

# Come Back
cd ..
