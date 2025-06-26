# teiknical_ashleylutz
teikobio technical interview

# Launching the application  
In order to generate the app, from within the repo ru the command streamlit run app.py
    - this will launch the streamlit application from which the user can add/drop samples, generate cell frequencies, run a Mann U test on the relative cell frequencies between responers and nonresponders, plot boxplots and conduct further grouping to determine counts of subset of intrerest

# Explain the schema 
- The schema is derived from the csv used to generate it in the create_db function. This optimizes flexibility as the same function could be used to generate schemas and dbs for different output. For each column in the csv the name, dtype and whether or not there were any NA values for that column in the input data is mapped to reflect the same characteristics in the schema. 
- To scale this schema effectively I would change it so that the cell type columns where melted, creating one column for cell type, with all the original column names as values and another for the measurement values from these original columns. I would also add a assay_value column to identify what assay these values reflect, in the case that multiple assays are conducted on the same sample.
- This long form would also make it easier to subset data for statistial analyses; specifically I would be interested in multivariate comparisons on individual assay values between responders, nonrepsonders, and healthy. And how these values change in each group over time 
- I would also be interested in the relationshops between assay values (specifically in this example different cell types) this would provide context for the mechanism of action belying the response

# Code structure 
- load_db contains all the functionality for creating, loading, and accessing the db these functions can then be called from the streamlit app (app.py) to allow the user to query, add and remove samples to the db
    - There were some assumptions made for the add/remove functionality; specifically that samples would be added from a CSV and removed via a list of sample_id strings 
- cellcount_analysis contains all the functional code for conducting the specific statistical tests and plots asked for in this tutorial. To scale this these functions could be made more generalizeable to take in any assay values, stratfy over time, or compare other groups (different medications, sick to healthy, ect)
- app.py runs the streamlit app through which the user can interact with the data and analyses 



