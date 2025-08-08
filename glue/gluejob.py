import sys
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame

# Job setup
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Temp paths
spark._jsc.hadoopConfiguration().set("spark.sql.warehouse.dir", "s3://tbsmcore/glue-temp/")
spark._jsc.hadoopConfiguration().set("hadoop.tmp.dir", "s3://tbsm-core/glue-temp/")

# Config
database_name = "pizzachain-rds-tbsm-db"
s3_output_base = "s3://pizzachain-curated-data-tbsm/"

# -------- Step 1: sku_master --------
sku_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_sku_master"
).toDF()

sku_df = sku_df.filter("sku_id != ''") \
    .withColumn("item_name", trim(lower(col("item_name")))) \
    .withColumn("category", trim(lower(col("category")))) \
    .withColumn("price", col("price").cast("double"))

# -------- Step 2: discounts --------
discounts_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_discounts_applied"
).toDF()

discounts_df = discounts_df.filter("discount_code != ''") \
    .withColumn("discount_code", trim(col("discount_code"))) \
    .withColumn("line_discount_amount", col("discount_amount").cast("double")) \
    .drop("discount_amount")

# -------- Step 3: orders_items --------
order_items_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_order_items"
).toDF()

order_items_df = order_items_df.filter(
    "order_id != '' AND sku_id != '' AND discount_code != '' AND quantity IS NOT NULL AND unit_price IS NOT NULL AND quantity != 0 AND unit_price != 0"
) \
    .withColumn("quantity", col("quantity").cast("int")) \
    .withColumn("unit_price", col("unit_price").cast("double")) \
    .withColumn("item_total", col("quantity") * col("unit_price")) \
    .join(sku_df, on="sku_id", how="inner") \
    .join(discounts_df.select("discount_code", "line_discount_amount"), on="discount_code", how="inner")

# -------- Step 4: orders --------
orders_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_orders"
).toDF()

orders_df = orders_df.filter("order_id != ''")

order_totals = order_items_df.groupBy("order_id").agg(
    sum("item_total").alias("order_total"),
    sum("line_discount_amount").alias("total_discount_amount")
)

orders_df = orders_df.join(order_totals, on="order_id", how="left") \
    .withColumn("day_of_week", date_format(to_date("order_time"), "EEEE"))

# -------- Step 5: inventory_stock --------
inventory_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_inventory_logs"
).toDF()

inventory_df = inventory_df.filter(
    "sku_id != '' AND store_id IS NOT NULL AND current_stock IS NOT NULL AND current_stock != 0"
) \
    .withColumnRenamed("current_stock", "stock_qty") \
    .withColumn("stock_qty", col("stock_qty").cast("int")) \
    .join(sku_df.select("sku_id", "price"), on="sku_id", how="inner") \
    .withColumn("stock_value", col("stock_qty") * col("price"))

# -------- Step 6: store --------
store_df = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, table_name="pizzachain_store_manager"
).toDF()

# -------- All Writes at the End --------
sku_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_sku_master/")
discounts_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_discounts/")
order_items_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_orders_items/")
orders_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_orders/")
inventory_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_inventory_stock/")
store_df.write.mode("overwrite").parquet(s3_output_base + "pizzadb_stores/")

# Commit the job
job.commit()
