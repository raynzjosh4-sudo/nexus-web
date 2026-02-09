// Community Data Module
console.log('community-data.js loaded');

// Community posts data
let COMMUNITY_POSTS = [];

// Initialize globally
window.COMMUNITY_POSTS = COMMUNITY_POSTS;

// Fetch community posts from Supabase
async function fetchCommunityPostsFromDB() {
    try {
        // Wait for Supabase to be available
        let attempts = 0;
        while (!window.supabase && attempts < 50) {
            await new Promise(r => setTimeout(r, 100));
            attempts++;
        }

        if (!window.supabase) {
            console.warn('Supabase not loaded, using empty data');
            window.COMMUNITY_POSTS = [];
            return;
        }

        // Create Supabase client
        const supabaseClient = window.supabase.createClient(
            'https://tdyebwcyamsqnnivynuk.supabase.co',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkeWVid2N5YW1zcW5uaXZ5bnVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODY3NzQsImV4cCI6MjA4MzM0Njc3NH0.m_3QY9xMqohJRFalwf9PFRMDDHy-_d3gLTBC_U9tcYQ'
        );

        // Try to fetch from community_posts table
        const { data, error } = await supabaseClient
            .from('community_posts')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) {
            console.warn('Error fetching from community_posts:', error.message);
            window.COMMUNITY_POSTS = [];
            return;
        }

        if (data && data.length > 0) {
            // Transform database data to match expected format
            window.COMMUNITY_POSTS = data.map(post => ({
                id: post.id,
                title: post.title || 'Untitled',
                description: post.body || post.description || '',
                body: post.body || post.description || '',
                category: post.category || 'discussion',
                image: post.image_url || post.image,
                image_url: post.image_url || post.image,
                author: post.author_id ? `User ${post.author_id.substring(0, 8)}` : 'Anonymous',
                date: post.created_at ? new Date(post.created_at).toLocaleDateString() : 'Unknown date',
                created_at: post.created_at,
                views: post.view_count || 0,
                replies: post.reply_count || post.comments || 0
            }));
            console.log('Loaded', window.COMMUNITY_POSTS.length, 'posts from database');
        } else {
            console.log('No community posts found in database');
            window.COMMUNITY_POSTS = [];
        }
    } catch (error) {
        console.error('Error in fetchCommunityPostsFromDB:', error);
        window.COMMUNITY_POSTS = [];
    }
}

// Export for use
window.COMMUNITY_POSTS = COMMUNITY_POSTS;
window.fetchCommunityPostsFromDB = fetchCommunityPostsFromDB;
