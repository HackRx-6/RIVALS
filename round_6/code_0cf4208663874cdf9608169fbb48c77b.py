with open('round_6/.gitignore', 'w') as f:
    f.write('''
# Ignore Python bytecode
__pycache__/
*.pyc
*.pyo
*.pyd

# Ignore input/output files
*.in
*.out
*.log
*.tmp
'''.lstrip())