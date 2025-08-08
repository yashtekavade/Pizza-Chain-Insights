# AWS Glue Jobs

This directory contains ETL job scripts for data processing.

## Files:
- `gluejob.py` - Main ETL job that:
  - Reads data from RDS
  - Applies transformations
  - Writes processed data to S3
  - Updates Glue Data Catalog

## Transformations:
1. Orders - Remove missing records, add derived columns
2. Order Items - Clean data, join with SKU master
3. SKU Master - Clean names and categories
4. Discounts Applied - Clean discount codes
5. Inventory Logs - Calculate stock values, enrich with product info
