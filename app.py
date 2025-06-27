import streamlit as st 
import os
import sqlite3
import pandas as pd
from load_db import load_csv_to_db, add_sample, remove_samples, create_db, load_db, get_column_names
from cellcount_analysis import cell_count_frequency, run_stats_on_cell_frequencies, plot_responders_vs_nonresponders

db_path = "data/cell_counts.db"
csv_path = "data/cell-count.csv"
cell_cols = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte", "sample"]

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}. Creating new database...")
    create_db(db_path)
else:
    print(f"Database found at {db_path}.")

# setting all display values to None 
if "df_freq" not in st.session_state:
    st.session_state.df_freq = None
if "stats_df" not in st.session_state:
    st.session_state.stats_df = None
if "fig" not in st.session_state:
    st.session_state.fig = None
if "df" not in st.session_state:
    st.session_state.df = None
if "agg_df" not in st.session_state: 
    st.session_state.agg_df = None

st.title("Cell Sample Manager and Analyzer")

# Section 1: Add a sample
st.header("Add Sample")
with st.form("add_form"):
    input_path = st.text_input("path to new data")
    submitted = st.form_submit_button("Add Sample")
    if submitted:
        # add samples 
        add_sample(db_path, input_path)
        st.success(f"Samples from {input_path} added.")

# Section 2: Remove a sample
st.header("Remove Sample")
sample_ids_to_remove = st.text_input("Sample IDs to remove")
if st.button("Remove Sample"):
    # covert samples string to list 
    sample_ids_to_remove = [s.strip() for s in sample_ids_to_remove.split(',')]
    # call remove function 
    remove_samples(db_path, sample_ids_to_remove)
    st.warning(f"Samples {sample_ids_to_remove} removed.")


# Section 3: Compute and show relative frequencies
st.header("Compute Relative Frequencies")
if st.button("Calculate Frequencies"):
    # reload db so that we get any changes that were added/dropped
    st.session_state.db = load_db(db_path)
    df = pd.read_sql("SELECT * FROM cell_counts", st.session_state.db)
    df_freq = cell_count_frequency(df, cell_cols)
    # save variables to session 
    st.session_state.df_freq=df_freq
    st.session_state.df=df
    st.session_state.db.close()

# show dataframe 
if st.session_state.df_freq is not None:
    st.subheader("Relative Frequencies")
    st.dataframe(st.session_state.df_freq)

# Section 4: Run stats
st.header("Calculate Cell Type Stats")
if st.button("Run Stats"):
    if st.session_state.df_freq is not None: 
        stats_df, test_df = run_stats_on_cell_frequencies(st.session_state.df_freq, st.session_state.df, cell_cols)
        # save variables to session 
        stats_df = stats_df.reset_index().style.background_gradient(subset=["pvalue"], cmap="RdYlGn_r")
        st.session_state.stats_df=stats_df
        st.session_state.test_df=test_df
    else : 
        st.warning("Generate relative cell frequencuies before running stats")

# show dataframe
if st.session_state.stats_df is not None:
    st.subheader("Stats Output")
    st.dataframe(st.session_state.stats_df)


# Section 5: Plot results
st.header("Plot Cell Type Frequencies")
if st.button("Plot Boxplots"):
    if st.session_state.stats_df is not None:
        fig = plot_responders_vs_nonresponders( st.session_state.test_df, st.session_state.stats_df.data)
        st.session_state.fig = fig
        
    else : 
        st.warning("Generate stats before plotting")

# show figure 
if st.session_state.fig is not None:
    st.subheader("Boxplots of cell types")
    st.plotly_chart(st.session_state.fig)

# add in a multiselect for users to continue to assess their data 
if st.session_state.df is not None:
    # reload db so that it can be accessed in this thread 
    db = load_db(db_path)
    # create set of potential group cols 
    group_cols = st.multiselect(
        "Group by one or more columns:",
        options = get_column_names(db, "cell_counts"),
        default=["sample_type"]
    )
    # create set of potential count cols 
    count_cols = st.multiselect(
        "Count values of what for a given group",
        options = get_column_names(db, "cell_counts"),
        default=["sample"]
    )

    if group_cols:
        if count_cols: 
            # make sure that group and count calls are disjoint 
            if set(group_cols).isdisjoint(set(count_cols)): 
                grouped_df = st.session_state.df.groupby(group_cols)[count_cols].count().reset_index()
                st.subheader("Grouped Results")
                st.session_state.agg_df = st.dataframe(grouped_df)
            else : 
                st.warning("cannot group by columns you are trying to count")

