import pandas as pd
import sqlite3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cas import is_valid_cas

COLUMNS = ["cas", "chemical_name", "list_name", "endpoint", "source_url", "retrieved"]
RAW = "data/lists/raw/"
RETRIEVED = "2026-10-17"


def clean_cas(df, list_name):
    rows_in = len(df)

    df["cas"] = df["cas"].fillna("")
    df["cas"] = df["cas"].str.split(r"[;/,\n]")
    df = df.explode("cas")
    df["cas"] = df["cas"].str.replace(" ", "")

    empty = df["cas"].isin(["", "-", "--", "---"])
    no_cas = empty.sum()
    df = df[~empty]

    is_valid = df["cas"].apply(is_valid_cas)
    invalid = (~is_valid).sum()
    df = df[is_valid]

    df = df.drop_duplicates()

    counts = {
        "list": list_name,
        "rows_in": rows_in,
        "no_cas": int(no_cas),
        "invalid": int(invalid),
        "kept": len(df),
    }

    return df, counts


def read_prop65():
    prop65 = pd.read_excel(RAW + "p65chemicalslist.xlsx", skiprows=11, dtype=str)
    prop65 = prop65[prop65["Type of Toxicity"].notna()].copy()
    delisted = prop65["Chemical"].str.contains("Delisted", na=False)
    n_delisted = delisted.sum()
    prop65 = prop65[~delisted].copy()
    print("Prop 65 delisted rows dropped:", n_delisted)

    # Endpoints removed by OEHHA but still in the file (see docs/sources.md)
    toluene_female = (prop65["CAS No."] == "108-88-3") & (prop65["Type of Toxicity"].str.strip() == "female")
    prop65 = prop65[~toluene_female].copy()
    prop65.loc[prop65["CAS No."] == "94-82-6", "Type of Toxicity"] = "male"
    prop65["Type of Toxicity"] = prop65["Type of Toxicity"].str.strip()

    prop65 = prop65.rename(columns={"Chemical": "chemical_name", "CAS No.": "cas", "Type of Toxicity": "endpoint"})
    prop65["list_name"] = "Prop 65"
    prop65["source_url"] = "https://oehha.ca.gov/proposition-65/proposition-65-list/"
    prop65["retrieved"] = RETRIEVED
    prop65 = prop65[COLUMNS]
    return clean_cas(prop65, "Prop 65")


def read_svhc():
    svhc = pd.read_excel(RAW + "candidate-list-of-svhc-for-authorisation-export.xlsx", skiprows=3, dtype=str)
    svhc = svhc.rename(columns={"Substance name": "chemical_name", "CAS No.": "cas", "Reason for inclusion": "endpoint"})
    svhc["list_name"] = "EU SVHC"
    svhc["source_url"] = "https://echa.europa.eu/candidate-list-table"
    svhc["retrieved"] = RETRIEVED
    svhc = svhc[COLUMNS]
    return clean_cas(svhc, "EU SVHC")


def make_endpoint(row):
    health = row["Health effects"] == "Yes"
    environment = row["Environmental effects"] == "Yes"
    if health and environment:
        return "health, environment"
    elif health:
        return "health"
    elif environment:
        return "environment"
    else:
        return ""


def read_ed_list(filename, list_name):
    ed_list = pd.read_excel(RAW + filename, skiprows=0, dtype=str)
    ed_list["endpoint"] = ed_list.apply(make_endpoint, axis=1)
    ed_list = ed_list[ed_list["endpoint"] != ""].copy()
    ed_list = ed_list.rename(columns={"Name and abbreviation": "chemical_name", "CAS no.": "cas"})
    ed_list["list_name"] = list_name
    ed_list["source_url"] = "https://edlists.org/"
    ed_list["retrieved"] = RETRIEVED
    ed_list = ed_list[COLUMNS]
    return clean_cas(ed_list, list_name)


def read_scil():
    workbook = pd.ExcelFile(RAW + "safer_chemical_ingredients_list.xls")
    sheets = []
    for sheet in workbook.sheet_names:
        if sheet == "UPDATES":
            continue
        one = pd.read_excel(workbook, sheet_name=sheet, dtype=str)
        one["function"] = sheet
        sheets.append(one)
    df = pd.concat(sheets, ignore_index=True)

    df = df.rename(columns={
        "CAS": "cas",
        "List Name": "chemical_name",
        "List Call": "rating",
    })
    df["list_name"] = "EPA SCIL"
    df["endpoint"] = ""
    df["source_url"] = "https://www.epa.gov/saferchoice/safer-ingredients"
    df["retrieved"] = RETRIEVED

    df = df[COLUMNS + ["rating", "function"]]
    return clean_cas(df, "EPA SCIL")


def main():
    tables = []
    all_counts = []

    readers = [
        read_prop65(),
        read_svhc(),
        read_ed_list("list1.xlsx", "EU ED List I"),
        read_ed_list("list2.xlsx", "EU ED List II"),
        read_ed_list("list3.xlsx", "EU ED List III"),
    ]
    for table, counts in readers:
        tables.append(table)
        all_counts.append(counts)

    hazard_list = pd.concat(tables, ignore_index=True)
    safer_list, scil_counts = read_scil()
    all_counts.append(scil_counts)

    con = sqlite3.connect("data/hazard.db")
    hazard_list.to_sql("hazard_list", con, if_exists="replace", index=False)
    safer_list.to_sql("safer_list", con, if_exists="replace", index=False)
    con.close()

    for counts in all_counts:
        print(counts)
    print(hazard_list["list_name"].value_counts())


if __name__ == "__main__":
    main()