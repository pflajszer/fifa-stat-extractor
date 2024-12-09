import easyocr

from models.data_loader import prelabel_images
base_folder = f"/app/db/fifa/stat-extractor/data"
src_folder = "/app/db/fifa/session_stats"
processed_folder = f"{base_folder}/V1/3.prelabelled/_UNLABELLED"
prelabelled_folder = f"{base_folder}/V1/5.prelabelled_tmp"
    
reader = easyocr.Reader(['en'])
prelabel_images(processed_folder, prelabelled_folder, reader, min_confidence=0.5)