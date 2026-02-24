import { useState, useEffect } from 'react';
import { View, Text, Image, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { supabase, LostItem } from '@/services/supabase';
import Colors from '@/constants/Colors';

export default function LostItemDetailScreen() {
    const { id } = useLocalSearchParams();
    const [item, setItem] = useState<LostItem | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadItem();
    }, [id]);

    const loadItem = async () => {
        try {
            const { data, error } = await supabase
                .from('lost_items')
                .select('*')
                .eq('id', id)
                .single();

            if (error) throw error;
            setItem(data);
        } catch (error) {
            console.error('Error loading item:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <View style={styles.centered}>
                <ActivityIndicator size="large" color={Colors.primary} />
            </View>
        );
    }

    if (!item) {
        return (
            <View style={styles.centered}>
                <Text style={styles.errorText}>Item not found</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.content}>
                <Text style={styles.status}>{item.status}</Text>
                <Text style={styles.title}>{item.title}</Text>
                {item.image_url && (
                    <Image source={{ uri: item.image_url }} style={styles.image} />
                )}
                <Text style={styles.body}>{item.description}</Text>
                {item.location && (
                    <View style={styles.infoRow}>
                        <Text style={styles.label}>Location:</Text>
                        <Text style={styles.value}>{item.location}</Text>
                    </View>
                )}
                {item.date_lost && (
                    <View style={styles.infoRow}>
                        <Text style={styles.label}>Date Lost:</Text>
                        <Text style={styles.value}>{new Date(item.date_lost).toLocaleDateString()}</Text>
                    </View>
                )}
                <View style={styles.infoRow}>
                    <Text style={styles.label}>Category:</Text>
                    <Text style={styles.value}>{item.category}</Text>
                </View>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    centered: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: Colors.background,
    },
    content: {
        padding: 16,
    },
    status: {
        fontSize: 12,
        color: Colors.secondary,
        textTransform: 'uppercase',
        marginBottom: 8,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 16,
    },
    image: {
        width: '100%',
        height: 200,
        borderRadius: 12,
        marginBottom: 16,
    },
    body: {
        fontSize: 16,
        color: Colors.text,
        lineHeight: 24,
        marginBottom: 24,
    },
    infoRow: {
        flexDirection: 'row',
        marginBottom: 12,
    },
    label: {
        fontSize: 14,
        color: Colors.secondary,
        fontWeight: '600',
        width: 100,
    },
    value: {
        fontSize: 14,
        color: Colors.text,
        flex: 1,
    },
    errorText: {
        color: Colors.primary,
        fontSize: 16,
    },
});
