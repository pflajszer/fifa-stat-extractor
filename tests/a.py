from utils import extract_stats_from_sliced_images
from easyocr import Reader
import pandas as pd

reader = Reader(["en"]) 
dest_dir = "/app/db/fifa/session_stats/2024-08-19/2024-08-19-0/DEFENDING"
stats = extract_stats_from_sliced_images(dest_dir, reader)


df = pd.read_csv("/app/tests/via_project_5Dec2024_23h22m_csv.csv")
df = df[["filename", "region_attributes"]]
df['filename'] = df['filename'].apply(lambda x: x.replace(x[0], "/"))
print(df.head())

for i in stats:
    x = df[df["ocr"].str.contains(i)]
    y = x["transcription"].iloc[0]
    y_hat = stats[i]
    print(y, y_hat, y==y_hat)
    assert y == y_hat
    
    
    
    https://www.robots.ox.ac.uk/~vgg/software/via/via_demo.html - here is the place we can annotate fairly simply...