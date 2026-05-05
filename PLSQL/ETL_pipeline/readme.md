# ETL Validation Package — Oracle PL/SQL

A PL/SQL package built on Oracle Database that automates data quality
validation across core ETL tables. It logs errors, tracks execution
via an audit trail, and provides summary reporting and resolution tools.

---

## Overview

This package (etl_validation_pkg) was designed as part of a broader
ETL framework to catch data issues early — before bad data propagates
downstream. It validates three core tables, writes structured error
records, and maintains a full audit log of every validation run.

---

## Database Objects

| Object                  | Type  | Description                                      |
|-------------------------|-------|--------------------------------------------------|
|  customers              | Table | Customer profiles and registration data          |
|  products               | Table | Product catalogue with pricing and stock levels  |
|  sales_transactions     | Table | Sales records linking customers to products      |
|  data_quality_errors    | Table | Error log for all failed validation checks       |
|  etl_audit_log          | Table | Execution history for all ETL processes          |
|  etl_validation_pkg     | Package | Validation logic, utilities, and reporting     |

---

## Package API

### Procedures

| Procedure                  | Parameters               | Description                                      |
|----------------------------|--------------------------|--------------------------------------------------|
|  run_all_validations       |  p_batch_id NUMBER       | Runs all validations in sequence                 |
|  validate_customers        |  p_batch_id NUMBER       | Validates the customers table                    |
|  validate_products         |  p_batch_id NUMBER       | Validates the products table                     |
|  validate_sales            |  p_batch_id NUMBER       | Validates the sales_transactions table           |
|  log_validation_result     | table, column, type, value, record_id | Writes a single error record      |
|  mark_errors_resolved      |  p_error_ids VARCHAR2    | Marks comma-separated error IDs as resolved      |

### Functions

| Function                   | Parameters               | Returns   | Description                           |
|----------------------------|--------------------------|-----------|---------------------------------------|
|  get_error_count           |  p_table_name VARCHAR2   |  NUMBER   | Returns unresolved error count        |
|  get_validation_summary    |  p_batch_id NUMBER       |  VARCHAR2 | Returns a formatted summary string    |

---

## Validation Rules

### Customers
- Email must match standard format (regex)
- First name and last name must not be null
- Email must be unique across all customer records

### Products
- Price must not be negative
- Stock quantity must not be negative
- Product name must not be null or blank
- Price must not exceed 10,000 (business rule)

### Sales Transactions
- Customer ID must reference a valid customer record
- Product ID must reference a valid product record
- Quantity must be greater than zero
- Transaction date must not be a future date
- Unit price must not deviate more than 10% from the product s listed price

---

## How to Use

Run all validations for a given batch:

--sql
BEGIN
    etl_validation_pkg.run_all_validations(p_batch_id => 1);
END;
