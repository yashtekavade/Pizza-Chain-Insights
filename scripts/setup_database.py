#!/usr/bin/env python3
"""
Database Setup Script for Pizza Chain Insights
Creates tables and loads sample data into RDS/MySQL database
"""

import mysql.connector
import pandas as pd
import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, host, user, password, database=None, port=3306):
        """Initialize database connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            if self.database:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    autocommit=False
                )
            else:
                # Connect without database to create it
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    autocommit=False
                )
            
            self.cursor = self.connection.cursor()
            logger.info(f"Successfully connected to MySQL server at {self.host}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False

    def create_database(self, db_name='pizza_chain_insights'):
        """Create database if it doesn't exist"""
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            self.cursor.execute(f"USE {db_name}")
            self.connection.commit()
            logger.info(f"Database '{db_name}' created/selected successfully")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Error creating database: {e}")
            return False

    def execute_sql_file(self, sql_file_path):
        """Execute SQL commands from a file"""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Split SQL commands by semicolon and execute
            sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for command in sql_commands:
                if command.upper().startswith(('CREATE', 'DROP', 'ALTER', 'INSERT')):
                    try:
                        self.cursor.execute(command)
                        logger.info(f"Executed: {command[:50]}...")
                    except mysql.connector.Error as e:
                        logger.warning(f"Warning executing command: {e}")
                        continue
            
            self.connection.commit()
            logger.info(f"Successfully executed SQL file: {sql_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing SQL file: {e}")
            self.connection.rollback()
            return False

    def load_csv_to_table(self, csv_file_path, table_name, batch_size=1000):
        """Load CSV data into database table"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loading {len(df)} rows from {csv_file_path} to table {table_name}")
            
            # Prepare column names and placeholders
            columns = df.columns.tolist()
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            # Insert query
            insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples for batch insert
            data_tuples = [tuple(row) for row in df.values]
            
            # Insert data in batches
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i + batch_size]
                self.cursor.executemany(insert_query, batch)
                logger.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} rows)")
            
            self.connection.commit()
            logger.info(f"Successfully loaded {len(df)} rows into {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV to table: {e}")
            self.connection.rollback()
            return False

    def validate_data_load(self):
        """Validate that data was loaded correctly"""
        try:
            tables = ['sku_master', 'discounts_applied', 'orders', 'order_items', 'inventory_logs']
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                logger.info(f"Table {table}: {count} rows")
            
            # Run some sample queries
            logger.info("\nRunning validation queries...")
            
            # Check for orders with items
            self.cursor.execute("""
                SELECT COUNT(DISTINCT o.order_id) as orders_with_items
                FROM orders o 
                INNER JOIN order_items oi ON o.order_id = oi.order_id
            """)
            result = self.cursor.fetchone()[0]
            logger.info(f"Orders with items: {result}")
            
            # Check inventory logs by store
            self.cursor.execute("""
                SELECT store_id, COUNT(*) as log_count
                FROM inventory_logs 
                GROUP BY store_id 
                LIMIT 5
            """)
            results = self.cursor.fetchall()
            logger.info("Sample inventory logs by store:")
            for store_id, count in results:
                logger.info(f"  Store {store_id}: {count} logs")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False

    def close_connection(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")

def main():
    """Main function to set up database and load data"""
    
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',  # Change to your RDS endpoint
        'user': 'root',       # Change to your database user
        'password': 'password',  # Change to your database password
        'port': 3306
    }
    
    # Paths
    SCHEMA_FILE = 'data/schemas/database_schema.sql'
    DATA_DIR = 'data/sample'
    
    # CSV files to load (in order due to foreign key constraints)
    CSV_FILES = [
        ('sku_master.csv', 'sku_master'),
        ('discounts_applied.csv', 'discounts_applied'),
        ('orders.csv', 'orders'),
        ('order_items.csv', 'order_items'),
        ('inventory_logs.csv', 'inventory_logs')
    ]
    
    # Initialize database setup
    db_setup = DatabaseSetup(**DB_CONFIG)
    
    try:
        # Connect to database
        if not db_setup.connect():
            sys.exit(1)
        
        # Create database
        if not db_setup.create_database():
            sys.exit(1)
        
        # Execute schema file
        if os.path.exists(SCHEMA_FILE):
            if not db_setup.execute_sql_file(SCHEMA_FILE):
                sys.exit(1)
        else:
            logger.error(f"Schema file not found: {SCHEMA_FILE}")
            sys.exit(1)
        
        # Load CSV data
        for csv_file, table_name in CSV_FILES:
            csv_path = os.path.join(DATA_DIR, csv_file)
            if os.path.exists(csv_path):
                if not db_setup.load_csv_to_table(csv_path, table_name):
                    logger.error(f"Failed to load {csv_file}")
                    continue
            else:
                logger.warning(f"CSV file not found: {csv_path}")
        
        # Validate data load
        db_setup.validate_data_load()
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)
    
    finally:
        db_setup.close_connection()

if __name__ == "__main__":
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("""
Pizza Chain Database Setup Script

Usage:
    python setup_database.py [options]

Options:
    --help          Show this help message
    --generate      Generate sample data first

Environment Variables:
    DB_HOST         Database host (default: localhost)
    DB_USER         Database user (default: root)
    DB_PASSWORD     Database password (default: password)
    DB_PORT         Database port (default: 3306)

Example:
    export DB_HOST=your-rds-endpoint.amazonaws.com
    export DB_USER=admin
    export DB_PASSWORD=your-password
    python setup_database.py
            """)
            sys.exit(0)
        elif sys.argv[1] == "--generate":
            logger.info("Generating sample data first...")
            import subprocess
            subprocess.run([sys.executable, "generate_pizza_chain_data.py"])
    
    # Override default config with environment variables
    import os
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    
    main()
