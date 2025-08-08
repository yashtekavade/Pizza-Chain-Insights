# Pizza Chain Insights

A cloud-native batch analytics pipeline for multi-branch pizza retail chain operational data analysis.

## 🎯 Project Overview

PizzaChain Insights is a comprehensive AWS-based data analytics solution that processes operational data from multiple pizza store locations, providing actionable insights for inventory management, sales analysis, and operational optimization.

### Business Challenge
- Process multi-store operational data (orders, inventory, discounts)
- Provide real-time insights for business decision making
- Automate alerts for operational risks (low inventory, revenue targets)
- Scale across multiple store locations

### Architecture Flow
```
Amazon RDS → AWS Glue → S3 → Athena ← Lambda → SQS → EC2 → SNS
```

## 🏗️ Repository Structure

```
Pizza-Chain-Insights/
├── README.md                     # Project overview and setup
├── scripts/                      # Data generation and setup scripts
│   ├── generate_pizza_chain_data.py
│   └── setup_database.py
├── data/                         # Data schemas
│   └── database_schema.sql
├── glue/                         # ETL processing scripts
│   └── gluejob.py
├── athena/                       # Business analytics queries
│   └── all queries.txt
├── lambda/                       # Serverless alert functions
│   └── lambdacode.py
├── ec2/                          # Dashboard application
│   └── ec2sqstosns.py
└── docs/                         # Project documentation
    └── Yashvardhan_Tekavade_AWS_Project_3.pdf
```

## 📊 Data Pipeline

### Data Flow
1. **Data Ingestion**: Operational data stored in Amazon RDS
2. **ETL Processing**: AWS Glue extracts, transforms, and loads data to S3
3. **Data Cataloging**: AWS Glue Data Catalog for schema management
4. **Analytics**: Amazon Athena for SQL-based analysis
5. **Alerting**: Lambda functions monitor thresholds and send alerts via SQS
6. **Notifications**: EC2 instances process alerts and send SNS notifications

### Core Business Questions
1. Top 5 Selling SKUs per Store (Last 7 Days)
2. Category-wise Revenue Breakdown with Discounts
3. Orders with High Discounts (>30% of total value)
4. Low Inventory Alerts based on weekend sales patterns
5. Revenue and Orders by Hour of Day

## �️ Data Schema

### Tables
- **orders**: Customer orders with store and timing information
- **order_items**: Individual items within orders
- **sku_master**: Product catalog with categories and pricing
- **discounts_applied**: Discount codes and amounts
- **inventory_logs**: Real-time inventory tracking

## 🚀 Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Python 3.8+
- AWS CLI configured
- Terraform (optional, for infrastructure as code)

### Quick Setup
1. Clone the repository
2. Set up AWS credentials
3. Run data generation scripts
4. Deploy infrastructure using provided scripts
5. Execute ETL pipelines

## 📁 Project Structure
```
├── data/                    # Sample data and schemas
├── scripts/                 # Database setup and data loading
├── glue/                   # AWS Glue ETL jobs
├── lambda/                 # Lambda functions for monitoring
├── athena/                 # SQL queries for analysis
├── ec2/                    # EC2 dashboard and notification service
├── infrastructure/         # Terraform/CloudFormation templates
├── docs/                   # Documentation and diagrams
└── config/                 # Configuration files
```

## 🔧 Implementation Tasks

- [ ] Database setup and data loading scripts
- [ ] AWS Glue ETL jobs for data transformation
- [ ] Athena queries for business analytics
- [ ] Lambda functions for threshold monitoring
- [ ] SQS queue setup for alert messaging
- [ ] EC2 service for SNS notifications
- [ ] Dashboard for KPI visualization

## 📈 Key Features

- **Batch Processing**: Efficient handling of large datasets
- **Real-time Monitoring**: Automated threshold-based alerts
- **Scalable Architecture**: Cloud-native design for growth
- **Security**: IAM roles and secure data handling
- **Modular Design**: Extensible for additional analytics needs

## 🛠️ Technologies Used

- **AWS RDS**: Operational data storage
- **AWS Glue**: ETL processing and data cataloging
- **Amazon S3**: Data lake storage
- **Amazon Athena**: SQL-based analytics
- **AWS Lambda**: Serverless monitoring functions
- **Amazon SQS**: Message queuing for alerts
- **Amazon SNS**: Notification delivery
- **Amazon EC2**: Dashboard hosting and alert processing

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.