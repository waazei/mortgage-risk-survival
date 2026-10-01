import pandas as pd
import zipfile
from io import TextIOWrapper


LOAN_ID = "F16Q10000190"

outer_zip = "data/raw/2016/historical_data_2016.zip"
inner_zip_name = "historical_data_2016Q1.zip"
perf_file = "perf_2016Q1.txt"


print("===== OPEN OUTER ZIP =====")

with zipfile.ZipFile(outer_zip, "r") as outer:

    print("Opening:", inner_zip_name)

    with outer.open(inner_zip_name) as inner_file:

        # Inner ZIP nằm bên trong outer ZIP
        inner_data = inner_file.read()

        print("Inner ZIP loaded.")

        with zipfile.ZipFile(
            __import__("io").BytesIO(inner_data),
            "r"
        ) as inner_zip:

            print("\n===== FILES IN INNER ZIP =====")

            print(
                inner_zip.namelist()
            )

            print("\n===== READING PERFORMANCE =====")

            with inner_zip.open(perf_file) as f:

                text_file = TextIOWrapper(
                    f,
                    encoding="latin1"
                )

                # Đọc header
                header = text_file.readline()

                print("\nHeader:")
                print(header)

                # Đọc từng dòng để tìm loan_id
                matches = []

                for line in text_file:

                    if line.startswith(LOAN_ID):

                        matches.append(
                            line.rstrip("\n")
                        )

                print(
                    "\nNumber of matching rows:",
                    len(matches)
                )

                print(
                    "\n===== MATCHING RAW ROWS ====="
                )

                for row in matches:
                    print(row)

print("\n===== DONE =====")