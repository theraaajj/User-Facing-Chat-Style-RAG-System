@echo off
cd "C:\Users\user\OneDrive\Desktop\SpiderWeb Technologies"
call spiderweb\Scripts\activate.bat
python data_pipeline\downloader.py
python data_pipeline\processor.py
python data_pipeline\uploader.py
