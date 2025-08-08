# EC2 Dashboard

This directory contains the dashboard application for SQS processing and SNS notifications.

## Files:
- `ec2sqstosns.py` - Main application that:
  - Reads messages from SQS queue
  - Processes alerts and notifications
  - Sends SNS notifications to stores
  - Provides monitoring interface

## Purpose:
- Process SQS messages from Lambda
- Send SNS notifications to stores
- Monitor operational alerts
