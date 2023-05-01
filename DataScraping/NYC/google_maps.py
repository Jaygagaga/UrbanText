import pandas as pd
import os
import subprocess

# get street names
output_file_name = './Data/nyc_streets.csv'
if not os.path.exists(output_file_name):
    df = pd.read_csv("./Data/List of street names - Streets.csv")
    df[df["City"] == "New York City"].to_csv(output_file_name, index=False)

# get public space names
output_file_name = './Data/nyc_public_space.csv'
if not os.path.exists(output_file_name):
    df = pd.read_csv("./Data/List of public spaces.csv")
    # change the first column name to "Street"
    df = df.rename(columns={df.columns[0]: "Street"})
    df[df["City"] == "New York City"].to_csv(output_file_name, index=False)

# merge the two csv files
street_df = pd.read_csv("./Data/nyc_streets.csv")
public_space_df = pd.read_csv("./Data/nyc_public_space.csv")
street_df = public_space_df.append(street_df)
# save the merged csv file
street_df.to_csv("./Data/nyc_streets_merged.csv", index=False)

# run google review scraper using subprocess.Popen
cmd = ['python', './DataScraping/GoogleMapReview.py', '-f', './Data/nyc_streets_merged.csv', '-c', 'New York City', 
       '-s', './Data/Reviews/GoogleMap', '-option', 
       'street_urls', '-u', './Data/Reviews/GoogleMap/unfound_public_space_reviews_GoogleMap.txt',
       '-driver', './Data/chrome_driver/chromedriver',
       '-ff', './Data/Reviews/GoogleMap/found_public_space_reviews_GoogleMap.txt']

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Print the output line by line as it computes
for line in iter(process.stdout.readline, ''):
    print(line.strip())
process.stdout.close()
process.wait()
