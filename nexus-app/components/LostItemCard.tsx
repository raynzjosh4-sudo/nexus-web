import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '@/constants/Colors';
import { LostItem } from '@/services/supabase';

interface LostItemCardProps {
    item: LostItem;
}

export default function LostItemCard({ item }: LostItemCardProps) {
    const router = useRouter();

    return (
        <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/lost-found/${item.id}`)}
        >
            <View style={styles.content}>
                <View style={styles.textContent}>
                    <Text style={styles.meta}>
                        {item.location} · {new Date(item.created_at).toLocaleDateString()}
                    </Text>
                    <Text style={styles.title}>{item.title}</Text>
                    <Text style={styles.description} numberOfLines={3}>
                        {item.description}
                    </Text>
                    <Text style={styles.status}>{item.status}</Text>
                </View>
                {item.image_url && (
                    <Image source={{ uri: item.image_url }} style={styles.image} />
                )}
            </View>
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: Colors.card,
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    content: {
        flexDirection: 'row',
        gap: 16,
    },
    textContent: {
        flex: 1,
    },
    meta: {
        fontSize: 12,
        color: Colors.secondary,
        marginBottom: 4,
    },
    title: {
        fontSize: 18,
        fontWeight: '600',
        color: Colors.primary,
        marginBottom: 8,
    },
    description: {
        fontSize: 14,
        color: Colors.textSecondary,
        lineHeight: 20,
        marginBottom: 8,
    },
    status: {
        fontSize: 12,
        color: Colors.secondary,
        textTransform: 'uppercase',
    },
    image: {
        width: 120,
        height: 90,
        borderRadius: 8,
    },
});
