import sys
with open('execution_log.txt', 'w') as f:
    f.write(f'Python execution successful at {sys.version}\n')
print('Script finished writing to execution_log.txt')
