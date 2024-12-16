from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, mean, stddev, abs as spark_abs
from pyspark.ml.feature import VectorAssembler, MinMaxScaler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
import time

spark = SparkSession.builder \
    .appName("PySpark_RF_Hyperparameter_Tuning") \
    .config("spark.default.parallelism", "48") \
    .config("spark.sql.shuffle.partitions", "48") \
    .getOrCreate()

file_path = '/home/zkw/pyspark_1/Agrofood_co2_emission_synthetic_500k.csv'
data = spark.read.csv(file_path, header=True, inferSchema=True)

columns_to_drop = ['Area', 'Year', 'Rural population', 'Urban population', 'Total Population - Male', 'Total Population - Female']
data = data.drop(*columns_to_drop)

imputed_cols = [col for col in data.columns if col != 'total_emission']
data = data.select(*[when(col(c).isNotNull(), col(c)).otherwise(lit(None)).alias(c) for c in data.columns])

for c in imputed_cols:
    mean_value = data.select(mean(c)).collect()[0][0]
    data = data.fillna({c: mean_value})

stats = data.select(*[mean(c).alias(f"{c}_mean") for c in imputed_cols] +
                    [stddev(c).alias(f"{c}_std") for c in imputed_cols]).collect()[0]

for c in imputed_cols:
    mean_val = stats[f"{c}_mean"]
    std_val = stats[f"{c}_std"]
    threshold = 3
    data = data.withColumn(c, when(spark_abs((col(c) - mean_val) / std_val) > threshold, mean_val).otherwise(col(c)))

if 'Average Temperature' in data.columns:
    assembler_temp = VectorAssembler(inputCols=['Average Temperature'], outputCol='temp_vec')
    scaler_temp = MinMaxScaler(inputCol='temp_vec', outputCol='scaled_temp')
    temp_model = scaler_temp.fit(assembler_temp.transform(data))
    from pyspark.sql.functions import udf
    from pyspark.sql.types import DoubleType

    extract_temp_udf = udf(lambda x: float(x[0]) if x is not None else None, DoubleType())
    data = temp_model.transform(assembler_temp.transform(data)).withColumn('Average Temperature', extract_temp_udf(col('scaled_temp')))
    data = data.drop('temp_vec', 'scaled_temp')

data = data.withColumn('Transport_Household_Ratio',
                       col('Food Transport') / (col('Food Household Consumption') + lit(1e-5)))

columns_to_drop_2 = ['Total Population', 'Food Household Consumption', 'Food Transport']
data = data.drop(*columns_to_drop_2)

assembler = VectorAssembler(inputCols=[c for c in data.columns if c != 'total_emission'], outputCol='features')
data = assembler.transform(data)

scaler = MinMaxScaler(inputCol='features', outputCol='scaled_features')
scaler_model = scaler.fit(data)
data = scaler_model.transform(data)

train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

rf = RandomForestRegressor(featuresCol='scaled_features', labelCol='total_emission', seed=42)

start_time = time.time()
rf_model = rf.fit(train_data)
train_time = time.time() - start_time

print(f"Model Training Time: {train_time:.4f} seconds")

predictions = rf_model.transform(test_data)

evaluator_mae = RegressionEvaluator(labelCol='total_emission', predictionCol='prediction', metricName='mae')
mae = evaluator_mae.evaluate(predictions)

r2 = RegressionEvaluator(labelCol='total_emission', predictionCol='prediction', metricName='r2').evaluate(predictions)

print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"R-squared (R²): {r2:.4f}")

spark.stop()
