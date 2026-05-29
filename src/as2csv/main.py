import io
import warnings
from enum import Enum
from getpass import getpass
from pathlib import Path

import msoffcrypto
import pandas as pd
import typer
from msoffcrypto.exceptions import DecryptionError

warnings.filterwarnings("ignore")

app = typer.Typer()


def db_converter(filename: Path):
    try:
        with open(filename, "rb") as file:
            decrypted_workbook = io.BytesIO(file.read())
        df = pd.read_excel(decrypted_workbook)

        df = df.iloc[:, 1:]
        match_df = df.iloc[:, 0].str.match("[0-9]{2}/[0-9]{2}/[0-9]{4}")
        idx = match_df.loc[match_df].index.min()
        new_df = df[match_df]
        new_df.columns = df.iloc[idx - 1]
        filepath = Path("db_transactions.csv")
        new_df.to_csv(filepath, index=False)
    except Exception as e:
        print(f"Unable to convert: {e}")


def sbi_converter(filename: Path):
    try:
        decrypted_workbook = io.BytesIO()
        with open(filename, "rb") as file:
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password=getpass(prompt="Password: "))
            office_file.decrypt(decrypted_workbook)
        df = pd.read_excel(decrypted_workbook)

        match_df = df.iloc[:, 0].str.match("[0-9]{2}/[0-9]{2}/[0-9]{4}")
        idx = match_df.loc[match_df].index.min()
        new_df = df[match_df]
        new_df.columns = df.iloc[idx - 1]
        new_df["Details"] = new_df["Details"].str.replace("   ", " ").str.replace("\n ", "").str.strip()

        filepath = Path("sbi_transactions.csv")
        new_df.to_csv(filepath, index=False)
    except DecryptionError as _:
        print("Wrong password!!!")
    except Exception as e:
        print(f"Unable to convert: {e}")


class ConverterType(str, Enum):
    db = "db"
    sbi = "sbi"


@app.command()
def main(converter: ConverterType, filename: Path):
    match converter:
        case ConverterType.db:
            db_converter(filename)
        case ConverterType.sbi:
            sbi_converter(filename)


if __name__ == "__main__":
    app()
