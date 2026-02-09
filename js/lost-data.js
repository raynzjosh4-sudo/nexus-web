// Lost & Found Data Module
console.log('lost-data.js loaded');

// Mock data export (will be populated by fetchLostItemsFromDB)
let MOCK_LOST_ITEMS = [
    // Sample data for testing with Cloudinary URLs
    {
        id: 'test-1',
        title: 'Black Samsung Phone',
        description: 'Lost black Samsung Galaxy S21 with a cracked screen protector. Last seen at the mall parking lot.',
        snippet: 'Lost black Samsung Galaxy S21 with a cracked screen protector.',
        category: 'devices',
        image: 'https://picsum.photos/400/300?random=1',
        location: 'South Gate Mall Parking',
        date: '2/8/2026',
        contact: 'info@example.com',
        status: 'open',
        views: 45
    },
    {
        id: 'test-2',
        title: 'Red Leather Wallet',
        description: 'Lost red leather wallet containing credit cards and ID. Very sentimental value.',
        snippet: 'Lost red leather wallet containing credit cards and ID.',
        category: 'accessories',
        image: 'https://picsum.photos/400/300?random=2',
        location: 'Downtown Area',
        date: '2/7/2026',
        contact: 'user@example.com',
        status: 'open',
        views: 32
    }
];

// Initialize globally
window.MOCK_LOST_ITEMS = MOCK_LOST_ITEMS;

// Fetch lost items from Supabase
async function fetchLostItemsFromDB() {
    try {
        // Wait for Supabase to be available
        let attempts = 0;
        while (!window.supabase && attempts < 50) {
            await new Promise(r => setTimeout(r, 100));
            attempts++;
        }

        if (!window.supabase) {
            console.warn('Supabase not loaded, using empty data');
            window.MOCK_LOST_ITEMS = [];
            return;
        }

        // Create Supabase client
        const supabaseClient = window.supabase.createClient(
            'https://tdyebwcyamsqnnivynuk.supabase.co',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkeWVid2N5YW1zcW5uaXZ5bnVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODY3NzQsImV4cCI6MjA4MzM0Njc3NH0.m_3QY9xMqohJRFalwf9PFRMDDHy-_d3gLTBC_U9tcYQ'
        );

        // Try to fetch from lost_found_items table
        const { data, error } = await supabaseClient
            .from('lost_found_items')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) {
            console.warn('Error fetching from lost_found_items:', error.message);
            // Fallback to empty array
            window.MOCK_LOST_ITEMS = [];
            return;
        }

        if (data && data.length > 0) {
            // Transform database data to match expected format
            window.MOCK_LOST_ITEMS = data.map((item, index) => {
                // Build image URL from Cloudinary ID
                let imageUrl = null;
                const CLOUDINARY_CLOUD_NAME = 'df8w2fain';

                // Try multiple image field names
                const possibleImageIds = [item.image_url, item.image, item.imageUrl];
                for (const imageId of possibleImageIds) {
                    if (imageId && typeof imageId === 'string' && imageId.trim()) {
                        // If it already starts with http, use as-is
                        if (imageId.startsWith('http')) {
                            imageUrl = imageId;
                            break;
                        } else {
                            // Otherwise, treat as Cloudinary public ID and construct URL
                            imageUrl = `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}/image/upload/w_400,h_300,c_fill/${imageId}`;
                            break;
                        }
                    }
                }

                // Use placeholder if no valid URL found (NULL values)
                // Removed: Just leave imageUrl as null if no image exists

                return {
                    id: item.id,
                    title: item.title || 'Untitled',
                    description: item.description || '',
                    snippet: item.description || '',
                    category: item.category || 'other',
                    image: imageUrl,
                    imageUrl: imageUrl,
                    location: item.location_name || 'Unknown',
                    date: item.item_date ? new Date(item.item_date).toLocaleDateString() : new Date(item.created_at).toLocaleDateString(),
                    dateAdded: item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Unknown',
                    contact: item.contact_value || 'Contact provided',
                    status: item.status || 'open',
                    views: item.view_count || 0
                };
            });
            console.log('Loaded', window.MOCK_LOST_ITEMS.length, 'items from database');
        } else {
            console.log('No lost items found in database');
            window.MOCK_LOST_ITEMS = [];
        }
    } catch (error) {
        console.error('Error in fetchLostItemsFromDB:', error);
        window.MOCK_LOST_ITEMS = [];
    }
}

// Export for use
window.MOCK_LOST_ITEMS = MOCK_LOST_ITEMS;
window.fetchLostItemsFromDB = fetchLostItemsFromDB;
