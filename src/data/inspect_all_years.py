from pathlib import Path
import zipfile


RAW_DIR = Path("data/raw")

YEARS = range(2016, 2027)


print("=" * 70)
print("CHECK FREDDIE MAC DATA 2016-2026")
print("=" * 70)


for year in YEARS:

    zip_file = RAW_DIR / str(year) / f"historical_data_{year}.zip"

    print("\n" + "-" * 70)
    print(f"YEAR: {year}")
    print(f"FILE: {zip_file}")

    if not zip_file.exists():
        print("Khong tim thay file!")
        continue

    try:
        with zipfile.ZipFile(zip_file, "r") as z:

            files = z.namelist()

            print(f"So file ben trong ZIP: {len(files)}")

            for file_name in files[:20]:
                print("  ", file_name)

            if len(files) > 20:
                print("  ...")

    except Exception as e:
        print(f"LOI: {e}")


print("\n" + "=" * 70)
print("DONE")
print("=" * 70)