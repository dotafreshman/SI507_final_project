# SI507 - Final Project

#### Research on Massive Shooting Violence in United States

## Data Source:

* Gun Violence Archive

  https://www.gunviolencearchive.org/reports/mass-shootings/2014

  - Description:

    Gun Violence Archive is an online public dataset website recording cases of gun violence in United States from 2000 to now. For this research, we use data of mass shooting in 2014. Mass shooting are defined as gun violence crime in which more or equal to 4 people get injured or killed. For each case, this dataset provides information including incident ID, date, state, city/country, address, and number of people injured and killed.

  - Access:

    Gun Violence Archive is open accessible to anyone. It has all data listed on the website in form of table. Data can be accessed with Beautifulsoup to scrape.

* Google Places API

  https://developers.google.com/places/web-service/search

  - Description:

    Google Places API is used to get detailed information of locations. In this research, we use Google Places API to obtain coordinates of the location we have from gun violence data.

  - Access:

    For Google Places API, the base url is https://maps.googleapis.com/maps/api/place/findplacefromtext/json?, input parameters are following:

    - `key` key of Google Places
    - `input` name of the location to search
    - `inputtype` use `textquery` to get a text form response
    - `fields` use `geometry` to get coordinate
## Additional Information
  There is a secret.py containing the keys for running this program. requirements.txt contains the packages needed
## Code Structure

- `plot1_map`

  This function is responsible for map plotting. It first select latitude, longitude and address information for all crimes happening in required state, and respectively store them in 3 different lists `lat_list`, `lng_list`, and `address_list`. Then we use for loop and plotly function to plot all crime address in a map. Middle of the map is selected with the first element of `lat_list` and `lng_list`.

- `plot2_box`

  Users input a list of states which they want to see visualization, then the injured number feature of crimes in these states will be retrieved. The data is transformed into dataframe called `df`, with only 2 columns, state and victims. Then we use function `px.box` to plot statistics including maximum, median and minimum injured of crimes in these states with box plot. 

- `plot3_line`

  We aggregate data of all crimes according to date. Then we retrieve data from database in the certain month that the user orders, in dataframe `df`, with 3 columns marking date, and number of injury and killed in this day. The we use line chart to visualize number of victims change along with day in the month. We use color to encode injury and killed.

- `plot4_bar`

  This function calculate number of crimes in each state, and order them descending. User inputs number n, and the function will show the number of crimes in first n state with a bar chart.

## User Guide

This program supports 4 types of graphs, map, box plot, line chart and bar chart. Using each of them can follow the below guide

- map: `map <alpha-2 state>`
  - first parameter show type of the graph map
  -  second parameter controls the state which you want to see data. State name is in alpha 2 code

- box plot: `box <list of state>`
  - first parameter show type of the graph box plot
  - second parameters are list of states you want to see data in. State name is in alpha 2 code, and different state should be separated by space
- line chart: `line <month>`
  - first parameter show type of the graph line chart
  - second parameters is the month you want to see data in. The month name should begin with capital letter
-  bar chart `bar <limit>`
  - first parameter show type of the graph bar chart
  - second parameter controls number of state you want to see data in.

`help` command can show  the commands supported by the program. `exit` can quit the program.
