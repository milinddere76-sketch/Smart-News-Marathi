@echo off
echo --- Git Status --- > git_trace.log
git status >> git_trace.log 2>&1
echo --- Git Branch --- >> git_trace.log
git branch >> git_trace.log 2>&1
echo --- Adding Files --- >> git_trace.log
git add . >> git_trace.log 2>&1
echo --- Committing --- >> git_trace.log
git commit -m "Ensure render.yaml is added" >> git_trace.log 2>&1
echo --- Setting Main Branch --- >> git_trace.log
git branch -M main >> git_trace.log 2>&1
echo --- Pushing --- >> git_trace.log
git push -u origin main --force >> git_trace.log 2>&1
echo --- Done --- >> git_trace.log
