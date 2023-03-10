import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    #create a SparkSession object in ApacheSpark
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    song_data =  input_data + 'song_data/*/*/*/*.json'
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'year', 'duration') \
                    .dropduplicates()
    song_tables.createOrReplaceTempView('songs')
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(os.path.join(output_data, 'songs'), partitionBy['year', 'artist_id'])

    # extract columns to create artists table
    artists_table = df.select(['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']).distinct()
    
    # write artists table to parquet files
    artists_table.write.parquet(os.path.join(output_data, 'artists/artists.parquet'), 'overwrite')


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    log_data = input_data + "log_data/*/*/*.json"

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df =df.where('page="NextSong"') 

    # extract columns for users table    
    users_table = df.select(["userId", "firstName", "lastName", "gender", "level"]).distinct()
    
    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, 'users/users.parquet'), 'overwrite')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: str(int(int(x)/1000)))
    df = df.withColumn('timestamp', get_timestamp(df.ts))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: str(datetime.fromtimestamp(int(x)/1000)))
    df = df.withColumn('datetime', get_datetime(df.ts))
    
    # extract columns to create time table
    time_table = df.select('datetime') \
                   .withColumn('start_time', df.datetime) \
                   .withColumn('hour', hour('datetime')) \
                   .withColumn('day', dayofmonth('datetime')) \
                   .withColumn('week', weekofyear('datetime')) \
                   .withColumn('month', month('datetime')) \
                   .withColumn('year', year('datetime')) \
                   .withColumn('weekday', dayofweek('datetime')) \
                   .dropDuplicates()
    
    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(os.path.join(output_data + 'time/' + 'time.parquet'), partitionBy=['year', 'month'])
    
    # read in song data to use for songplays table
    song_df = spark.read.json(input_data + 'song_data/*/*/*/*.json')

    # extract columns from joined song and log datasets to create songplays table 
    df = df.alias('df')
    song_df = song_df.alias('song_df')
    
#join the song and log data 
    combined_df = df.join(song_df, col('log_df.artist') == col('song_df.artist_name'), 'inner')
    
    
    songplays_table = combined_df.distinct() \
                                 .select(
                                         col('start_time'),
                                         col('userId'),
                                         col('level'),
                                         col('sessionId'),
                                         col('location'),
                                         col('userAgent'),
                                         col('song_id'),
                                         col('artist_id')) \
                                 .withColumn('songplay_id', monotonically_increasing_id())
    
    
    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy('year', 'month') \
                         .parquet(os.path.join(output_data,
                                 'songplays/songplays.parquet'),
                                 'overwrite')


def main():
    spark = create_spark_session()
    input_data = "s3://udacity-dend/"
    song_data = "s3a://udacity-dend/song_data/*/*/*/*.json"
    log_data  = "s3a://udacity-dend/log-data/*.json"
    output_data = "s3://my-udacity-dend/output/" 
    
    process_song_data(spark, song_data, output_data)    
    process_log_data(spark, log_data, output_data)


if __name__ == "__main__":
    main()
