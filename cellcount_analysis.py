import pandas as pd 
from scipy.stats import mannwhitneyu
import statsmodels.formula.api as smf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.stats.anova import anova_lm


def cell_count_frequency(df, cell_cols):
    # Calculate total counts per sample 
    cell_cols.remove("sample")
    total_counts = df.groupby("sample")[cell_cols].sum()
    total_counts["total_count"] = total_counts.sum(axis=1)
    
    #melt for long format so that each row is one celltype per sample 
    counts_long = total_counts.reset_index().melt(
        id_vars=["sample", "total_count"], 
        value_vars=cell_cols,
        var_name="cell_type",
        value_name="count"
    )
    
    # Calculate relative frequency
    counts_long["relative_frequency"] = round((counts_long["count"] / counts_long["total_count"]) * 100, 2)
    
    # Select and order columns
    counts_final = counts_long[["sample", "total_count", "cell_type", "count", "relative_frequency"]]
    
    return(counts_final)

def run_mannu_stats_on_cell_frequencies(counts_final, df, cell_cols):
    cell_cols.remove("sample")
    df_test= counts_final.merge(df.drop(cell_cols, axis=1)) # dropping to avoid nonrelative counts
    df_test = df_test.query("condition=='melanoma' & sample_type=='PBMC' & treatment=='miraclib'")
    repsonders = df_test.query("response=='yes'")
    nonresponders = df_test.query("response=='no'") # specifying no to avoid nas
    stat_dict = {}
    for c in cell_cols: 
        stat, p = mannwhitneyu(repsonders.query("cell_type==@c")["relative_frequency"], nonresponders.query("cell_type==@c")["relative_frequency"])
        stat_dict[c] = p
 
    return(stat_dict, df_test)

def run_stats_on_cell_frequencies(counts_final, df, cell_cols):
    cell_cols.remove("sample")
    df_test= counts_final.merge(df.drop(cell_cols, axis=1)) # dropping to avoid nonrelative counts
    df_test["time_from_treatment_start"] = df_test["time_from_treatment_start"].astype("category")
    df_test["cell_type"] = df_test["cell_type"].astype("category")
    df_test["relative_frequency"] = df_test["relative_frequency"]
    df_test = df_test.query("condition=='melanoma' & sample_type=='PBMC' & treatment=='miraclib'")
    stats_results = []

    for c in df_test["cell_type"].unique():
        df_cell = df_test.query("cell_type==@c")
        # Fit OLS model for ANOVA
        model = smf.ols("relative_frequency ~ C(response) * C(time_from_treatment_start)", data=df_cell).fit()
        anova_results = anova_lm(model, typ=2)  # Type II ANOVA

        # Add cell type to each row
        anova_results = anova_results.reset_index().rename(columns={'index': 'term'})
        anova_results["cell_type"] = c
        print(anova_results)
        stats_results.append(anova_results)
        
    stats_df = pd.concat(stats_results).dropna()
    stats_df=stats_df.rename({"PR(>F)" : "pvalue"}, axis=1)
    return(stats_df, df_test)

def plot_responders_vs_nonresponders(df_test, stats_df): 
    df_plot = df_test.copy()
    ncols = 3
    cell_types = df_plot["cell_type"].unique()
    nrows = -(-len(cell_types) // ncols)

    stat_dict = dict(zip(stats_df.query("term == 'C(response)'").cell_type.values, stats_df.query("term == 'C(response)'").pvalue.values))
    # make subplot since we want to plot each pval on each plot
    fig = make_subplots(
        rows=nrows,
        cols=ncols,
        subplot_titles=[f"{c} (p={stat_dict[c]:.3g})" for c in cell_types]
    )

    # Plot box plots into subplots
    for i, cell_type in enumerate(cell_types):
        row = i // ncols + 1
        col = i % ncols + 1

        sub_df = df_plot[df_plot["cell_type"] == cell_type]

        fig.add_trace(
            go.Box(
                x=sub_df["response"],
                y=sub_df["relative_frequency"],
                name=cell_type,
                boxmean=True
            ),
            row=row,
            col=col
        )

    # Final layout tweaks
    fig.update_layout(
        height=300 * nrows,
        width=1000,
        title_text="Cell Type Frequencies by Response",
        showlegend=False
    )

    fig.update_yaxes(title_text="Relative Frequency")
    fig.update_xaxes(title_text="Response")

    return(fig)
    #TODO add a print to styled pandas for stat_df