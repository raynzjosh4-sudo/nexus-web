import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import Colors from '@/constants/Colors';
import { CommunityPost } from '@/services/supabase';

interface CommunityCardProps {
    post: CommunityPost;
}

export default function CommunityCard({ post }: CommunityCardProps) {
    const router = useRouter();

    return (
        <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/community/${post.id}`)}
        >
            <View style={styles.content}>
                <View style={styles.textContent}>
                    <Text style={styles.meta}>
                        Nexus Community · {new Date(post.created_at).toLocaleDateString()}
                    </Text>
                    <Text style={styles.title}>{post.title}</Text>
                    <Text style={styles.description} numberOfLines={3}>
                        {post.body}
                    </Text>
                    <View style={styles.stats}>
                        <Text style={styles.stat}>👁️ {post.view_count} views</Text>
                        <Text style={styles.stat}>💬 {post.reply_count} replies</Text>
                    </View>
                </View>
                {post.image_url && (
                    <Image source={{ uri: post.image_url }} style={styles.image} />
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
        marginBottom: 12,
    },
    stats: {
        flexDirection: 'row',
        gap: 16,
    },
    stat: {
        fontSize: 12,
        color: Colors.secondary,
    },
    image: {
        width: 120,
        height: 90,
        borderRadius: 8,
    },
});
