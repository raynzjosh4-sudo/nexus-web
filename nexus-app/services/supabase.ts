import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://tdyebwcyamsqnnivynuk.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkeWVid2N5YW1zcW5uaXZ5bnVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODY3NzQsImV4cCI6MjA4MzM0Njc3NH0.m_3QY9xMqohJRFalwf9PFRMDDHy-_d3gLTBC_U9tcYQ';

export const supabase = createClient(supabaseUrl, supabaseKey);

export interface CommunityPost {
    id: string;
    title: string;
    body: string;
    category: string;
    image_url?: string;
    created_at: string;
    author_id: string;
    view_count: number;
    reply_count: number;
}

export interface LostItem {
    id: string;
    title: string;
    description: string;
    category: string;
    image_url?: string;
    location?: string;
    date_lost?: string;
    created_at: string;
    status: string;
}
