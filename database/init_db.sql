DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    tenure INT,
    monthly_charges NUMERIC(10, 2),
    contract VARCHAR(50),
    tech_support VARCHAR(3),
    churn VARCHAR(3)
);

INSERT INTO customers (customer_id, tenure, monthly_charges, contract, tech_support, churn)
VALUES 
    ('CUST-1001', 12, 55.50, 'Month-to-month', 'Yes', 'No'),
    ('CUST-1002', 2, 70.00, 'Month-to-month', 'No', 'Yes'),
    ('CUST-1003', NULL, 89.99, 'One year', 'Yes', 'No'),    
    ('CUST-1004', 24, 105.50, 'Two year', 'No', 'No'),
    ('CUST-1005', 1, NULL, 'Month-to-month', 'No', 'Yes'),   
    ('CUST-1006', 72, 115.25, 'Two year', 'Yes', 'No'),
    ('CUST-1007', 5, 45.00, 'Month-to-month', 'No', 'Yes');
