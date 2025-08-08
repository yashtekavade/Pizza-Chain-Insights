# Lambda Functions

This directory contains serverless functions for alerting and automation.

## Files:
- `lambdacode.py` - Main Lambda function for:
  - Threshold monitoring
  - SQS message processing
  - Athena query execution
  - Alert generation

## Purpose:
- Run scheduled Athena queries to check thresholds
- Send alerts to SQS for processing
- Trigger notifications for low inventory or other business rules
