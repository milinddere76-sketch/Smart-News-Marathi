import os

def update_presets(file_path, old_presets, new_preset):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old in old_presets:
        content = content.replace(f'"{old}"', f'"{new_preset}"')
        content = content.replace(f"'{old}'", f"'{new_preset}'")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {file_path}")

# Update video_generator.py
update_presets('d:/Apps/Smart News Marathi/backend/video_generator.py', ['veryfast'], 'ultrafast')

# Update anchor_generator.py
update_presets('d:/Apps/Smart News Marathi/backend/anchor_generator.py', ['fast'], 'ultrafast')
