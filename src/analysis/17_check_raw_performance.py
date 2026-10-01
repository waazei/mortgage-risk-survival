import pandas as pd
from pathlib import Path


LOAN_ID = "F16Q10000190"

path = Path(
    "data/raw/2016/historical_data_2016.zip"
)

print("Reading:", path)

# Đọc danh sách file trong ZIP
import zipfile

with zipfile.ZipFile(path, "r") as z:

    print("\n===== FILES IN ZIP =====")

    files = z.namelist()

    for f in files:
        print(f)

print("\n===== DONE =====")