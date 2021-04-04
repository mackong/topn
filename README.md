# Introduction
A simple app to calculate topn of most occured urls in a large file which cannot be loaded into memory directly.

# URL Dataset
The base url dataset is get from https://www.kaggle.com/shawon10/url-classification-dataset-dmoz,
which is *55MB*. then with some shell commands to get a 100GB file.
```
unzip 'URL Classification.csv.zip'
awk -F, 'print $2' 'URL Classification.csv' > urls.base.txt

# 100GB / 55MB ~= 1862

# Get the top 100 of base urls.
sort urls.base.txt | uniq -c | sort -rn | head -n 100 | awk '{print $1*1862, $2}' > expect.txt

# Concanate to 100GB
for i in {1..1862}
do
    cat urls.base.txt >> urls.txt
done
```
