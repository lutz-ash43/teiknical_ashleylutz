import sqlite3
import pandas as pd
import os


def map_dtype(dtype):
    # creating hardcoded mapping of dtypes 
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    else:
        return "TEXT"
    
def load_csv_to_db(db_path, csv_path):
    # read in csv and deposit into database 
    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    df.to_sql("cell_counts", conn, if_exists="append", index=False)
    conn.close()
    print("CSV data loaded into database.")


def create_db(db_path, csv_path):
    # create db and define schema flexibly for names, dtypes and nulls
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table if it exists (optional)
    cursor.execute("DROP TABLE IF EXISTS cell_counts")
    
    data = pd.read_csv(csv_path)
    # create dictionary for if columns have null values 
    null_dict = dict(zip(data.columns, [data[x].isna().any() for x in data.columns]))
    # rename nulls to be sql friendly 
    null_dict = {k: "NOT NULL" if not v else "" for k, v in null_dict.items()}
    
    table_name = "cell_counts"
    # create schema 
    db_cols = ",\n  ".join([
        f"{col} {map_dtype(dtype)} {null_dict[col]}"
        for col, dtype in zip(data.columns, data.dtypes)
        ])
    #print(db_cols)
    cursor.execute(f"""
    CREATE TABLE cell_counts (
        {db_cols}
    )
    """)
    # call function to load in csv 
    load_csv_to_db(db_path, csv_path)

    conn.commit()
    conn.close()
    print("Database initialized with schema.")



def add_sample(db_path, sample_data_path):
    # sample_data is a dict or DataFrame row
    db = sqlite3.connect(db_path)
    new_data = pd.DataFrame(sample_data_path) #assuming sample_data is a dataframe
    new_data.to_sql("cell_counts", db, if_exists="append", index=False)
    db.close()

def remove_samples(db_path, sample_ids):
    db = sqlite3.connect(db_path)
    if not sample_ids:
        print("No sample IDs provided.")
        return
    # create column separated list as a placeholder for input sample ids 
    placeholders = ','.join(['?'] * len(sample_ids))  
    query = f"DELETE FROM cell_counts WHERE sample IN ({placeholders})"
    cursor = db.cursor()
    cursor.execute(query, sample_ids)
    db.commit()

    # check to make sure samples existed 
    if cursor.rowcount == 0:
        print("No matching samples found.")
    else:
        print(f"{cursor.rowcount} sample(s) removed: {sample_ids}")
    db.close()

def load_db(db_path):
    # load db 
    db = sqlite3.connect("data/cell_counts.db")
    return(db)

def get_column_names(db, table_name):
    # get schema from db 
    cursor = db.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]  # row[1] is the column name
    return columns
