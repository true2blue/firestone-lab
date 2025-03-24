source ./venv/Scripts/activate
pip install pyinstaller
pyinstaller --noconfirm --clean run_app.spec
mkdir -p dist/logs
mkdir -p dist/config
cp -f config/config.ini dist/config