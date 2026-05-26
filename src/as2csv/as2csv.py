import argparse
import io
from getpass import getpass
from pathlib import Path

import msoffcrypto
import pandas as pd


def db_converter(filename: Path):
    with open(filename, "rb") as file:
        decrypted_workbook = io.BytesIO(file.read())
    df = pd.read_excel(decrypted_workbook)

    df = df.iloc[:, 1:]
    match_df = df.iloc[:, 0].str.match("[0-9]{2}/[0-9]{2}/[0-9]{4}")
    idx = match_df.loc[match_df].index.min()
    new_df = df[match_df]
    new_df.columns = df.iloc[idx - 1]
    filepath = Path("../../db_transactions.csv")
    new_df.to_csv(filepath, index=False)


def sbi_converter(filename: Path):
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

    filepath = Path("../../sbi_transactions.csv")
    new_df.to_csv(filepath, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("converter", type=str, choices=["db", "sbi"])
    parser.add_argument("filename", type=Path, action="store", help="import file path")
    args = parser.parse_args()

    match args.converter:
        case "db":
            db_converter(args.filename)
        case "sbi":
            sbi_converter(args.filename)
