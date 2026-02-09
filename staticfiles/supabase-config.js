// Supabase Configuration
console.log('supabase-config.js loaded');

// Initialize Supabase client
const supabaseUrl = window.SUPABASE_URL || 'https://tdyebwcyamsqnnivynuk.supabase.co';
const supabaseKey = window.SUPABASE_KEY || localStorage.getItem('supabase_key') || '';

// Create Supabase client if supabase JS library is available
if (typeof supabase !== 'undefined') {
    const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);
    window.supabaseClient = supabaseClient;
    console.log('Supabase initialized: success');
} else {
    console.warn('Supabase JS library not loaded');
}
