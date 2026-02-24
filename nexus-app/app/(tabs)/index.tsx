import { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import SearchBar from '@/components/SearchBar';
import CommunityCard from '@/components/CommunityCard';
import { fetchCommunityPosts, searchCommunityPosts } from '@/services/api';
import { CommunityPost } from '@/services/supabase';
import Colors from '@/constants/Colors';

const categories = [
    { id: 'all', label: 'All' },
    { id: 'request', label: 'Requests' },
    { id: 'discussion', label: 'Discussions' },
    { id: 'event', label: 'Events' },
    { id: 'question', label: 'Questions' },
    { id: 'recommendation', label: 'Recommendations' },
    { id: 'announcement', label: 'Announcements' },
];

export default function CommunityScreen() {
    const [posts, setPosts] = useState<CommunityPost[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');

    useEffect(() => {
        loadPosts();
    }, [selectedCategory]);

    const loadPosts = async () => {
        try {
            setLoading(true);
            const data = await fetchCommunityPosts(selectedCategory);
            setPosts(data);
        } catch (error) {
            console.error('Error loading posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (query: string) => {
        setSearchQuery(query);
        if (query.trim()) {
            try {
                const data = await searchCommunityPosts(query);
                setPosts(data);
            } catch (error) {
                console.error('Error searching:', error);
            }
        } else {
            loadPosts();
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <SearchBar
                    value={searchQuery}
                    onChangeText={handleSearch}
                    placeholder="Search community..."
                />
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabs}>
                    {categories.map((cat) => (
                        <TouchableOpacity
                            key={cat.id}
                            style={[styles.tab, selectedCategory === cat.id && styles.tabActive]}
                            onPress={() => setSelectedCategory(cat.id)}
                        >
                            <Text style={[styles.tabText, selectedCategory === cat.id && styles.tabTextActive]}>
                                {cat.label}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={Colors.primary} style={styles.loader} />
            ) : (
                <FlatList
                    data={posts}
                    renderItem={({ item }) => <CommunityCard post={item} />}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={
                        <Text style={styles.emptyText}>No posts found</Text>
                    }
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    header: {
        padding: 16,
        backgroundColor: Colors.header,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
    },
    tabs: {
        marginTop: 12,
    },
    tab: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        marginRight: 8,
        borderBottomWidth: 2,
        borderBottomColor: 'transparent',
    },
    tabActive: {
        borderBottomColor: Colors.primary,
    },
    tabText: {
        color: Colors.textSecondary,
        fontSize: 13,
    },
    tabTextActive: {
        color: Colors.primary,
        fontWeight: '600',
    },
    list: {
        padding: 16,
    },
    loader: {
        marginTop: 40,
    },
    emptyText: {
        textAlign: 'center',
        color: Colors.primary,
        fontSize: 16,
        marginTop: 40,
    },
});
