# teiknical_ashleylutz
teikobio technical interview

# Launching the application  
In order to generate the app, from within the repo ru the command ```streamlit run app.py```
- this will launch the streamlit application from which the user can add/drop samples, generate cell frequencies, run a Mann U test on the relative cell frequencies between responers and nonresponders, plot boxplots and conduct further grouping to determine counts of subset of intrerest
- default paths are set for this project but these can be specificed as arguments using the parameters --db_path, --csv_path, --cell_cols 

# Explain the schema 
- The schema is derived from the csv used to generate it in the create_db function. This optimizes flexibility as the same function could be used to generate schemas and dbs for different output. For each column in the csv the name, dtype and whether or not there were any NA values for that column in the input data is mapped to reflect the same characteristics in the schema. 
- To scale this schema effectively I would change it so that the cell type columns where melted, creating one column for cell type, with all the original column names as values and another for the measurement values from these original columns. I would also add a assay_value column to identify what assay these values reflect, in the case that multiple assays are conducted on the same sample.
- This long form would also make it easier to subset data for statistial analyses; specifically I would be interested in multivariate comparisons on individual assay values between responders, nonrepsonders, and healthy. And how these values change in each group over time 
- I would also be interested in the relationshops between assay values (specifically in this example different cell types) this would provide context for the mechanism of action belying the response

# Code structure 
- load_db contains all the functionality for creating, loading, and accessing the db these functions can then be called from the streamlit app (app.py) to allow the user to query, add and remove samples to the db
    - There were some assumptions made for the add/remove functionality; specifically that samples would be added from a CSV and removed via a string of comma separated sample ids 
- cellcount_analysis contains all the functional code for conducting the specific statistical tests and plots asked for in this tutorial. To scale this these functions could be made more generalizeable to take in any assay values, stratfy over time, or compare other groups (different medications, sick to healthy, ect)
    - I originally started the analysis as only a pairwise comparison between repsonders and nonresponders for each cell type frequency however after reflecting I thought the timing of the measures might affect these reuslts and be meaningful to the user. As such I switched to a multivariate model which assessed the affect of time and treatment. Ultimately the only significant effect was in the cd4_t_cells regardless of time so I only plotted the reuslts with respect to responder but as an extension to this app I would have made that a toggle by which the user can select to visualize the data stratified by time or not.  
- app.py runs the streamlit app through which the user can interact with the data and analyses.
      - the app begins by determining if the db has already been created and if not it creates it
      - otherwise there is functionality for the user to add/remove samples and conduct the analyses asked for. These analyses are hardcoded at the moment for the analyses asked for but to scale these would be made generalizeable with more parameterization.
      - at the bottom of the app the user can select columns to subset and filter from and then aggregate those columns to different counts. A future expansion would be allowing the user to select their own aggregation method.  



