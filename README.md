# Forechester #

Customer Survey Score predictor for CapSim
Calculates customer survey scores for each product month.
Uses input of html couriers by round.
Reverse-engineered from guidelines and analyst reports. 
Predict customer suvey score to forecast for market share and total units produced.

### Instructions ###

1. Download using `git clone` + GitHub repo link
2. Execute `python3 interface.py` in the terminal. Install any necessary extensions. This starts a flask dash server; navigate to browser to use the dashboard
3. Use the dropdowns at the top to select a round and segment (these selections currently only fetch the Industry 92 contained in `couriers/html`)
4. In the second data table, enter in predictions for products next round. For testing, use the button below the table to pre-fill it with real data from the next round
5. After entering data, click "Calculate Scores". This will create a visualization of the segment's position, a data table with a MoM breakdown of scoring, and a data table with EoY market share data.

- To test the accuracy of the prediction function, run `python3 tester.py` along with the necessary command line input. This loads all product data for an industry and compares predictions against actual results. There will be terminal output for each prediction, MoM data for fine-grained inspection, and a graph of all products located in `accuracy_graph.html`. Use the product index from hover data on graph or index in dataframe to select a product for fine-grained output.

- Sample Accuracy Test for Industry 93
![Screenshot 2024-03-04 at 9 53 58 AM](https://github.com/dkrill15/ForeChester/assets/71748033/f7561699-5431-47c4-84d6-46aec6f6e775)
- Sample Dashboard Test for Performance Segment in Round 3 of Industry 92
![Screenshot 2024-03-04 at 10 26 28 AM](https://github.com/dkrill15/ForeChester/assets/71748033/c52f5dfc-ee49-4c35-8c93-0dbb33f899ec)

### Files ###

##### forechester.py #####
contains main `score` function:
    params: product attributes
    return: list of customer survey scores by month

##### loader.py #####
contains helper functions that data from html and pdf couriers

##### functions.py #####
contains mathy functions called by `forechester.py` to calculate customer survey score


#### Current Bugs / Tickets ####
+ accessibility is still slightly off - average error > .02; salesmanship is not currently a factor
+ A/R policy is assumed to be 45 for all teams
+ code ugly af

