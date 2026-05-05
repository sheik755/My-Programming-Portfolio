create or replace PACKAGE etl_validation_pkg AS
    
    -- Main validation procedure (runs all validations)
    PROCEDURE run_all_validations(p_batch_id IN NUMBER);

    -- Individual validation procedures
    PROCEDURE validate_customers(p_batch_id IN NUMBER);
    PROCEDURE validate_products(p_batch_id IN NUMBER);
    PROCEDURE validate_sales(p_batch_id IN NUMBER);

    -- Data quality utilities
    PROCEDURE log_validation_result(
        p_table_name IN VARCHAR2,
        p_column_name IN VARCHAR2,
        p_error_type IN VARCHAR2,
        p_error_value IN VARCHAR2,
        p_record_id IN VARCHAR2
    );

    FUNCTION get_validation_summary(p_batch_id IN NUMBER) RETURN VARCHAR2;
    FUNCTION get_error_count(p_table_name IN VARCHAR2 DEFAULT NULL) RETURN NUMBER;
    PROCEDURE mark_errors_resolved(p_error_ids IN VARCHAR2);

END etl_validation_pkg;

create or replace PACKAGE BODY etl_validation_pkg AS
    
    -- Log validation results
    PROCEDURE log_validation_result(
        p_table_name IN VARCHAR2,
        p_column_name IN VARCHAR2,
        p_error_type IN VARCHAR2,
        p_error_value IN VARCHAR2,
        p_record_id IN VARCHAR2
    ) IS
    BEGIN
        INSERT INTO data_quality_errors (
            table_name, column_name, error_type, 
            error_value, record_id, error_date
        ) VALUES (
            p_table_name, p_column_name, p_error_type,
            p_error_value, p_record_id, SYSDATE
        );
        COMMIT;
    END log_validation_result;

    -- Run all validations
    PROCEDURE run_all_validations(p_batch_id IN NUMBER) IS
        v_log_id NUMBER;
        v_start_time TIMESTAMP;
    BEGIN
        v_start_time := CURRENT_TIMESTAMP;

        INSERT INTO etl_audit_log (
            process_name, step_name, status, start_time
        ) VALUES (
            'DATA_VALIDATION', 'RUN_ALL_VALIDATIONS', 'STARTED', v_start_time
        )
        RETURNING log_id INTO v_log_id;

        COMMIT;

        -- Run individual validations
        validate_customers(p_batch_id);
        validate_products(p_batch_id);
        validate_sales(p_batch_id);

        -- Update audit log
        UPDATE etl_audit_log 
        SET status = 'SUCCESS',
            end_time = CURRENT_TIMESTAMP,
            duration_seconds = EXTRACT(SECOND FROM (CURRENT_TIMESTAMP - v_start_time))
        WHERE log_id = v_log_id;

        COMMIT;

        DBMS_OUTPUT.PUT_LINE('All validations completed successfully.');

    EXCEPTION
        WHEN OTHERS THEN
            UPDATE etl_audit_log 
            SET status = 'ERROR',
                error_message = DBMS_UTILITY.FORMAT_ERROR_STACK,
                end_time = CURRENT_TIMESTAMP
            WHERE log_id = v_log_id;
            COMMIT;
            RAISE;
    END run_all_validations;

    -- Validate customers (already working)
    PROCEDURE validate_customers(p_batch_id IN NUMBER) IS
        v_error_count NUMBER := 0;
        v_log_id NUMBER;
        v_start_time TIMESTAMP;
    BEGIN
        v_start_time := CURRENT_TIMESTAMP;

        INSERT INTO etl_audit_log (
            process_name, step_name, status, start_time
        ) VALUES (
            'DATA_VALIDATION', 'VALIDATE_CUSTOMERS', 'STARTED', v_start_time
        )
        RETURNING log_id INTO v_log_id;

        COMMIT;

        -- Check 1: Invalid email format
        FOR rec IN (
            SELECT customer_id, email
            FROM customers
            WHERE NOT REGEXP_LIKE(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
        ) LOOP
            log_validation_result('CUSTOMERS', 'EMAIL', 'INVALID_FORMAT', rec.email, rec.customer_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 2: Missing required fields
        FOR rec IN (
            SELECT customer_id, first_name, last_name
            FROM customers
            WHERE first_name IS NULL OR last_name IS NULL
        ) LOOP
            log_validation_result('CUSTOMERS', 'NAME_FIELDS', 'MISSING_DATA', 
                'First: ' || NVL(rec.first_name, 'NULL') || ', Last: ' || NVL(rec.last_name, 'NULL'), 
                rec.customer_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 3: Duplicate emails
        FOR rec IN (
            SELECT customer_id, email, COUNT(*) OVER (PARTITION BY email) as dup_count
            FROM customers
        ) LOOP
            IF rec.dup_count > 1 THEN
                log_validation_result('CUSTOMERS', 'EMAIL', 'DUPLICATE_VALUE', rec.email, rec.customer_id);
                v_error_count := v_error_count + 1;
            END IF;
        END LOOP;

        -- Update audit log
        UPDATE etl_audit_log 
        SET status = 'SUCCESS',
            records_processed = v_error_count,
            end_time = CURRENT_TIMESTAMP,
            duration_seconds = EXTRACT(SECOND FROM (CURRENT_TIMESTAMP - v_start_time))
        WHERE log_id = v_log_id;

        COMMIT;

    EXCEPTION
        WHEN OTHERS THEN
            UPDATE etl_audit_log 
            SET status = 'ERROR',
                error_message = DBMS_UTILITY.FORMAT_ERROR_STACK,
                end_time = CURRENT_TIMESTAMP
            WHERE log_id = v_log_id;
            COMMIT;
            RAISE;
    END validate_customers;

    -- Validate products (already working)
    PROCEDURE validate_products(p_batch_id IN NUMBER) IS
        v_error_count NUMBER := 0;
        v_log_id NUMBER;
        v_start_time TIMESTAMP;
    BEGIN
        v_start_time := CURRENT_TIMESTAMP;

        INSERT INTO etl_audit_log (
            process_name, step_name, status, start_time
        ) VALUES (
            'DATA_VALIDATION', 'VALIDATE_PRODUCTS', 'STARTED', v_start_time
        )
        RETURNING log_id INTO v_log_id;

        COMMIT;

        -- Check 1: Negative price
        FOR rec IN (
            SELECT product_id, price
            FROM products
            WHERE price < 0
        ) LOOP
            log_validation_result('PRODUCTS', 'PRICE', 'NEGATIVE_VALUE', rec.price, rec.product_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 2: Negative stock
        FOR rec IN (
            SELECT product_id, stock_quantity
            FROM products
            WHERE stock_quantity < 0
        ) LOOP
            log_validation_result('PRODUCTS', 'STOCK_QUANTITY', 'NEGATIVE_VALUE', rec.stock_quantity, rec.product_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 3: Missing product name
        FOR rec IN (
            SELECT product_id, product_name
            FROM products
            WHERE product_name IS NULL OR TRIM(product_name) = ''
        ) LOOP
            log_validation_result('PRODUCTS', 'PRODUCT_NAME', 'MISSING_DATA', rec.product_name, rec.product_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 4: Price too high (business rule)
        FOR rec IN (
            SELECT product_id, price, product_name
            FROM products
            WHERE price > 10000
        ) LOOP
            log_validation_result('PRODUCTS', 'PRICE', 'EXCESSIVE_VALUE', rec.price || ' for ' || rec.product_name, rec.product_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Update audit log
        UPDATE etl_audit_log 
        SET status = 'SUCCESS',
            records_processed = v_error_count,
            end_time = CURRENT_TIMESTAMP,
            duration_seconds = EXTRACT(SECOND FROM (CURRENT_TIMESTAMP - v_start_time))
        WHERE log_id = v_log_id;

        COMMIT;

    EXCEPTION
        WHEN OTHERS THEN
            UPDATE etl_audit_log 
            SET status = 'ERROR',
                error_message = DBMS_UTILITY.FORMAT_ERROR_STACK,
                end_time = CURRENT_TIMESTAMP
            WHERE log_id = v_log_id;
            COMMIT;
            RAISE;
    END validate_products;

    -- NEW: Validate sales transactions
    PROCEDURE validate_sales(p_batch_id IN NUMBER) IS
        v_error_count NUMBER := 0;
        v_log_id NUMBER;
        v_start_time TIMESTAMP;
    BEGIN
        v_start_time := CURRENT_TIMESTAMP;

        INSERT INTO etl_audit_log (
            process_name, step_name, status, start_time
        ) VALUES (
            'DATA_VALIDATION', 'VALIDATE_SALES', 'STARTED', v_start_time
        )
        RETURNING log_id INTO v_log_id;

        COMMIT;

        -- Check 1: Invalid customer reference
        FOR rec IN (
            SELECT s.transaction_id, s.customer_id
            FROM sales_transactions s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        ) LOOP
            log_validation_result('SALES_TRANSACTIONS', 'CUSTOMER_ID', 'INVALID_REFERENCE', 
                rec.customer_id, rec.transaction_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 2: Invalid product reference
        FOR rec IN (
            SELECT s.transaction_id, s.product_id
            FROM sales_transactions s
            LEFT JOIN products p ON s.product_id = p.product_id
            WHERE p.product_id IS NULL
        ) LOOP
            log_validation_result('SALES_TRANSACTIONS', 'PRODUCT_ID', 'INVALID_REFERENCE', 
                rec.product_id, rec.transaction_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 3: Negative quantity
        FOR rec IN (
            SELECT transaction_id, quantity
            FROM sales_transactions
            WHERE quantity <= 0
        ) LOOP
            log_validation_result('SALES_TRANSACTIONS', 'QUANTITY', 'INVALID_VALUE', 
                rec.quantity, rec.transaction_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 4: Future transaction date
        FOR rec IN (
            SELECT transaction_id, transaction_date
            FROM sales_transactions
            WHERE transaction_date > SYSDATE
        ) LOOP
            log_validation_result('SALES_TRANSACTIONS', 'TRANSACTION_DATE', 'FUTURE_DATE', 
                TO_CHAR(rec.transaction_date, 'YYYY-MM-DD'), rec.transaction_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Check 5: Unit price mismatch with product price (tolerance 10%)
        FOR rec IN (
            SELECT s.transaction_id, s.unit_price, p.price as product_price,
                   ABS(s.unit_price - p.price) / p.price * 100 as price_diff_percent
            FROM sales_transactions s
            JOIN products p ON s.product_id = p.product_id
            WHERE ABS(s.unit_price - p.price) / p.price * 100 > 10
        ) LOOP
            log_validation_result('SALES_TRANSACTIONS', 'UNIT_PRICE', 'PRICE_MISMATCH', 
                'Sale: ' || rec.unit_price || ' vs Product: ' || rec.product_price || ' (' || ROUND(rec.price_diff_percent, 2) || '%)',
                rec.transaction_id);
            v_error_count := v_error_count + 1;
        END LOOP;

        -- Update audit log
        UPDATE etl_audit_log 
        SET status = 'SUCCESS',
            records_processed = v_error_count,
            end_time = CURRENT_TIMESTAMP,
            duration_seconds = EXTRACT(SECOND FROM (CURRENT_TIMESTAMP - v_start_time))
        WHERE log_id = v_log_id;

        COMMIT;

    EXCEPTION
        WHEN OTHERS THEN
            UPDATE etl_audit_log 
            SET status = 'ERROR',
                error_message = DBMS_UTILITY.FORMAT_ERROR_STACK,
                end_time = CURRENT_TIMESTAMP
            WHERE log_id = v_log_id;
            COMMIT;
            RAISE;
    END validate_sales;

    -- Get error count
    FUNCTION get_error_count(p_table_name IN VARCHAR2 DEFAULT NULL) RETURN NUMBER IS
        v_count NUMBER;
    BEGIN
        IF p_table_name IS NULL THEN
            SELECT COUNT(*) INTO v_count FROM data_quality_errors WHERE resolved = 'N';
        ELSE
            SELECT COUNT(*) INTO v_count 
            FROM data_quality_errors 
            WHERE table_name = p_table_name AND resolved = 'N';
        END IF;

        RETURN v_count;
    END get_error_count;

    -- Get validation summary
    FUNCTION get_validation_summary(p_batch_id IN NUMBER) RETURN VARCHAR2 IS
        v_summary VARCHAR2(4000);
        v_total_errors NUMBER;
        v_customer_errors NUMBER;
        v_product_errors NUMBER;
        v_sales_errors NUMBER;
    BEGIN
        v_total_errors := get_error_count(NULL);
        v_customer_errors := get_error_count('CUSTOMERS');
        v_product_errors := get_error_count('PRODUCTS');
        v_sales_errors := get_error_count('SALES_TRANSACTIONS');

        v_summary := 'Validation Summary:' || CHR(10) ||
                     'Total Errors: ' || v_total_errors || CHR(10) ||
                     'Customer Errors: ' || v_customer_errors || CHR(10) ||
                     'Product Errors: ' || v_product_errors || CHR(10) ||
                     'Sales Errors: ' || v_sales_errors;

        RETURN v_summary;
    END get_validation_summary;

    -- Mark errors as resolved
    PROCEDURE mark_errors_resolved(p_error_ids IN VARCHAR2) IS
        v_tab DBMS_UTILITY.UNCL_ARRAY;
        v_count NUMBER;
    BEGIN
        -- Split comma-separated string into array
        DBMS_UTILITY.COMMA_TO_TABLE(
            list   => p_error_ids,
            tablen => v_count,
            tab    => v_tab
        );
        
        -- Update using the array
        FOR i IN 1..v_count LOOP
            UPDATE data_quality_errors
            SET resolved = 'Y',
                error_date = SYSDATE
            WHERE error_id = TO_NUMBER(v_tab(i));
        END LOOP;
        
        COMMIT;
        
        DBMS_OUTPUT.PUT_LINE(v_count || ' errors marked as resolved.');
        
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Error marking errors as resolved: ' || SQLERRM);
            RAISE;
    END mark_errors_resolved;

END etl_validation_pkg;