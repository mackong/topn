#!/usr/bin/env bash

# The base url dataset is get from https://www.kaggle.com/shawon10/url-classification-dataset-dmoz

TARGET_SIZE=$((100 * 1024 * 1024 * 1024))  # 100GB
BASE_FILE=urls.base.txt
BASE_SIZE=`stat -c %s $BASE_FILE`
NSPLIT=$(($TARGET_SIZE/$BASE_SIZE + 1))

# Get the top 100 of base urls.
echo "Calculate the expect topn result into expect.txt."
sort urls.base.txt | uniq -c | sort -rn | head -n 100 | awk -v nsplit="$NSPLIT" '{print $1*nsplit, $2}' > expect.txt

# Concanate to 101GB
echo "Concanate final urls into urls.txt"
for (( i = 0; i <= $NSPLIT; i++ ))
do
    cat urls.base.txt >> urls.txt
done

echo "Done"
