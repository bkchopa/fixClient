from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "tkinter", "requests", "threading"],  # 필요한 패키지 추가
    "include_files": []  # 필요한 파일이 있다면 여기에 추가
}

setup(
    name="fixClient",
    version="0.1",
    description="fixClient Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")]  # GUI 애플리케이션의 경우 base="Win32GUI" 추가
)