## Project: Data Lake
### Introduction
A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The purpose of this project is to build an ETL pipeline that extracts their data from S3, processes the data using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow their analytics team to continue finding insights in what songs their users are listening to.

To test the database and you will run queries provided by the analytics team on ETL pipeline and compare your results with their expected results.

### Datasets
You'll be working with two datasets that reside in S3. Below is the link to the dataset.

Song data: s3://udacity-dend/song_data
Log data: s3://udacity-dend/log_data

### Project Files

etl.py - reads data from S3, processes that data using Spark, and writes them back to S3
dl.cfg - contains your AWS credentials
README.md provides discussion on your process and decisions.

### Process
1. Create IAM user and replace credentials in dl.cfg
2. Make sure to import required modules to be used in the project.
3. Make the necessary adjustments in input and output data file paths in etl.py file.
4. To test etl.py file  run 'python etl.py' in the terminal.




