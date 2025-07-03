-- BigCapital Database Schema Optimizations
-- This script applies performance optimizations for BigCapital

-- Set optimal MySQL settings for BigCapital
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864; -- 64MB
SET GLOBAL query_cache_type = 1;

-- Create indexes for common BigCapital queries (if tables exist)
-- Note: These will be created by BigCapital application, this is just for reference

-- Optimize for invoice queries
-- CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
-- CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON invoices(customer_id);
-- CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);

-- Optimize for expense queries  
-- CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
-- CREATE INDEX IF NOT EXISTS idx_expenses_vendor_id ON expenses(vendor_id);
-- CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);

-- Optimize for contact queries
-- CREATE INDEX IF NOT EXISTS idx_contacts_type ON contacts(contact_type);
-- CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);

-- Optimize for transaction queries
-- CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
-- CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

SELECT 'BigCapital database optimization script completed' as message;
