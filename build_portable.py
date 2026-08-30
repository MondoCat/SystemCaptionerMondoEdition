import os
import shutil
import PyInstaller.__main__
import faster_whisper

def build_portable():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    dist_path = os.path.join(current_dir, 'dist')
    build_path = os.path.join(current_dir, 'build')
    nvidia_deps_path = os.path.join(current_dir, 'nvidia_dependencies')
    icon_path = os.path.join(current_dir, 'icon.ico')
    
    faster_whisper_path = os.path.dirname(faster_whisper.__file__)
    assets_path = os.path.join(faster_whisper_path, 'assets')
    
    for path in [dist_path, build_path]:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=SystemCaptioner',
        '--onedir',
        f'--icon={icon_path}',
        '--noconsole',
        '--clean',
        '--add-data=icon.ico;.',
        '--add-data=cat.ico;.',
        '--add-data=border.png;.',
        '--add-data=cat.png;.',
        '--add-data=transcriber.py;.',
        '--add-data=recorder.py;.',
        '--add-data=console.py;.',
        f'--add-data={assets_path};faster_whisper/assets',
        '--hidden-import=queue',
        '--hidden-import=gui',
        '--hidden-import=configparser',
        '--hidden-import=customtkinter',
        '--hidden-import=setupGUI',
        '--hidden-import=torch',
        '--hidden-import=whisper',
        '--hidden-import=numpy',
        '--hidden-import=pyaudio',
        '--hidden-import=threading',
        '--hidden-import=transcriber',
        '--hidden-import=recorder',
        '--hidden-import=console',
        '--hidden-import=sounddevice',
        '--hidden-import=wave',
        '--hidden-import=scipy',
        '--hidden-import=faster_whisper',
        '--hidden-import=ctypes',
        '--hidden-import=win32gui',
        '--collect-all=whisper',
        '--collect-all=torch',
        '--collect-all=faster_whisper',
        '--collect-all=customtkinter',
    ])
    
    PyInstaller.__main__.run([
        'controller.py',
        '--name=Controller',
        '--onedir',
        f'--icon={icon_path}',
        '--noconsole',
        '--clean',
        f'--add-data={assets_path};faster_whisper/assets',
        '--hidden-import=queue',
        '--hidden-import=configparser',
        '--hidden-import=setupGUI',
        '--hidden-import=gui',
        '--hidden-import=torch',
        '--hidden-import=whisper',
        '--hidden-import=numpy',
        '--hidden-import=pyaudio',
        '--hidden-import=threading',
        '--hidden-import=transcriber',
        '--hidden-import=recorder',
        '--hidden-import=sounddevice',
        '--hidden-import=wave',
        '--hidden-import=scipy',
        '--hidden-import=faster_whisper',
        '--hidden-import=ctypes',
        '--hidden-import=win32gui',
        '--collect-all=whisper',
        '--collect-all=torch',
        '--collect-all=faster_whisper',
    ])
    
    if os.path.exists(nvidia_deps_path):
        target_nvidia_path = os.path.join(dist_path, 'SystemCaptioner', 'nvidia_dependencies')
        if os.path.exists(target_nvidia_path):
            shutil.rmtree(target_nvidia_path)
        shutil.copytree(nvidia_deps_path, target_nvidia_path)
        print("NVIDIA dependencies copied successfully")
    
    print("Build completed successfully!")
    
    try:
        dist_system_captioner = os.path.join(dist_path, 'SystemCaptioner')
        dist_controller = os.path.join(dist_path, 'Controller')
        controller_internal = os.path.join(dist_system_captioner, 'Controller', '_internal')
        
        if os.path.exists(dist_controller):
            target_controller = os.path.join(dist_system_captioner, 'Controller')
            if os.path.exists(target_controller):
                shutil.rmtree(target_controller)
            shutil.move(dist_controller, target_controller)
            print("Controller folder moved successfully")
        
        nvidia_src = os.path.join(dist_system_captioner, 'nvidia_dependencies')
        if os.path.exists(nvidia_src):
            nvidia_dest = os.path.join(controller_internal, 'nvidia_dependencies')
            if os.path.exists(nvidia_dest):
                shutil.rmtree(nvidia_dest)
            shutil.copytree(nvidia_src, nvidia_dest)
            print("NVIDIA dependencies copied to Controller/_internal successfully")
        
        icon_src = os.path.join(dist_system_captioner, '_internal', 'icon.ico')
        icon_dest = os.path.join(dist_system_captioner, 'icon.ico')
        if os.path.exists(icon_src):
            shutil.copy2(icon_src, icon_dest)
            print("icon.ico copied to root successfully")
        
        print("Post-build steps completed successfully!")
        
    except Exception as e:
        print(f"Error during post-build steps: {e}")

if __name__ == "__main__":
    build_portable()