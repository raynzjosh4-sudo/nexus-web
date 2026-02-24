import { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import SearchBar from '@/components/SearchBar';
import LostItemCard from '@/components/LostItemCard';
import { fetchLostItems } from '@/services/api';
import { LostItem } from '@/services/supabase';
import Colors from '@/constants/Colors';

const filters = [
    { id: 'all', label: 'All Items' },
    { id: 'documents', label: 'Documents' },
    { id: 'devices', label: 'Devices' },
    { id: 'accessories', label: 'Accessories' },
    { id: 'pet', label: 'Pets' },
];

export default function LostFoundScreen() {
    const [items, setItems] = useState<LostItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedFilter, setSelectedFilter] = useState('all');

    useEffect(() => {
        loadItems();
    }, [selectedFilter]);

    const loadItems = async () => {
        try {
            setLoading(true);
            const data = await fetchLostItems(selectedFilter);
            setItems(data);
        } catch (error) {
            console.error('Error loading items:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredItems = items.filter((item) =>
        searchQuery
            ? item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.description.toLowerCase().includes(searchQuery.toLowerCase())
            : true
    );

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <SearchBar
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    placeholder="Search lost items..."
                />
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabs}>
                    {filters.map((filter) => (
                        <TouchableOpacity
                            key={filter.id}
                            style={[styles.tab, selectedFilter === filter.id && styles.tabActive]}
                            onPress={() => setSelectedFilter(filter.id)}
                        >
                            <Text style={[styles.tabText, selectedFilter === filter.id && styles.tabTextActive]}>
                                {filter.label}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={Colors.primary} style={styles.loader} />
            ) : (
                <FlatList
                    data={filteredItems}
                    renderItem={({ item }) => <LostItemCard item={item} />}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={
                        <Text style={styles.emptyText}>No items found</Text>
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
