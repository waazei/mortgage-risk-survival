import zipfile
from pathlib import Path


ZIP_FILE = Path("data/raw/2026/historical_data_2026.zip")


def inspect_zip(zip_file):
    print("=" * 60)
    print("KIEM TRA FILE FREDDIE MAC")
    print("=" * 60)

    with zipfile.ZipFile(zip_file, "r") as outer_zip:

        print("\n[1] FILE BEN NGOAI:")
        for name in outer_zip.namelist():
            print(" -", name)

        nested_zip_name = outer_zip.namelist()[0]

        nested_data = outer_zip.read(nested_zip_name)

        print("\n[2] ZIP BEN TRONG:")
        print(" -", nested_zip_name)

        temp_zip = Path("temp_nested.zip")
        temp_zip.write_bytes(nested_data)

        with zipfile.ZipFile(temp_zip, "r") as inner_zip:

            for name in inner_zip.namelist():

                print("\nFILE:", name)

                with inner_zip.open(name) as f:

                    for i in range(3):
                        line = f.readline().decode(
                            "latin1"
                        ).strip()

                        print(f"Dong {i + 1}:")
                        print(line[:500])

        temp_zip.unlink()


if __name__ == "__main__":
    inspect_zip(ZIP_FILE)