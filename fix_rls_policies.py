"""
Fix RLS Policy for market_orders table

This script creates necessary Row-Level Security policies for the market_orders table
to allow authenticated users to insert their own orders.
"""

import os
from supabase import create_client, Client

# Initialize Supabase client
url: str = os.environ.get('SUPABASE_URL')
key: str = os.environ.get('SUPABASE_KEY')  # Service role key for admin operations
supabase: Client = create_client(url, key)

# SQL to create RLS policies for market_orders
policies_sql = """
-- Enable Row Level Security
ALTER TABLE market_orders ENABLE ROW LEVEL SECURITY;

-- Policy: Allow users to insert their own orders
CREATE POLICY "Users can insert their own orders" ON market_orders
    FOR INSERT 
    WITH CHECK (auth.uid() = buyer_id);

-- Policy: Allow users to view their own orders
CREATE POLICY "Users can view their own orders" ON market_orders
    FOR SELECT 
    USING (auth.uid() = buyer_id);

-- Policy: Allow users to update their own pending orders
CREATE POLICY "Users can update their own pending orders" ON market_orders
    FOR UPDATE 
    USING (auth.uid() = buyer_id AND status = 'PENDING')
    WITH CHECK (auth.uid() = buyer_id);
"""

print("Creating RLS policies...")
print(policies_sql)
print("\n" + "="*50)
print("IMPORTANT: These policies need to be created in Supabase Dashboard")
print("="*50)
print("\nSteps:")
print("1. Go to your Supabase Dashboard")
print("2. Navigate to Database > Policies")
print("3. Select the 'market_orders' table")
print("4. Click 'New Policy'")
print("5. Create each policy using the SQL above")
print("\n" + "="*50)
print("\nOR use SQL Editor to run the entire script above.")
print("="*50)
