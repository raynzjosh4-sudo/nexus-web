import { supabase, CommunityPost, LostItem } from './supabase';

export const fetchCommunityPosts = async (category?: string): Promise<CommunityPost[]> => {
    let query = supabase
        .from('community_posts')
        .select('*')
        .order('created_at', { ascending: false });

    if (category && category !== 'all') {
        query = query.eq('category', category);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data || [];
};

export const fetchLostItems = async (filter?: string): Promise<LostItem[]> => {
    let query = supabase
        .from('lost_items')
        .select('*')
        .order('created_at', { ascending: false });

    if (filter && filter !== 'all') {
        query = query.eq('category', filter);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data || [];
};

export const searchCommunityPosts = async (searchQuery: string): Promise<CommunityPost[]> => {
    const { data, error } = await supabase
        .from('community_posts')
        .select('*')
        .or(`title.ilike.%${searchQuery}%,body.ilike.%${searchQuery}%`)
        .order('created_at', { ascending: false });

    if (error) throw error;
    return data || [];
};
