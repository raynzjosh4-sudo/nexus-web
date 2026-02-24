import { useState, useEffect } from 'react';
import { View, Text, Image, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { supabase, CommunityPost } from '@/services/supabase';
import Colors from '@/constants/Colors';

export default function CommunityDetailScreen() {
    const { id } = useLocalSearchParams();
    const [post, setPost] = useState<CommunityPost | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPost();
    }, [id]);

    const loadPost = async () => {
        try {
            const { data, error } = await supabase
                .from('community_posts')
                .select('*')
                .eq('id', id)
                .single();

            if (error) throw error;
            setPost(data);
        } catch (error) {
            console.error('Error loading post:', error);
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

    if (!post) {
        return (
            <View style={styles.centered}>
                <Text style={styles.errorText}>Post not found</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.content}>
                <Text style={styles.meta}>
                    {new Date(post.created_at).toLocaleDateString()} · {post.category}
                </Text>
                <Text style={styles.title}>{post.title}</Text>
                {post.image_url && (
                    <Image source={{ uri: post.image_url }} style={styles.image} />
                )}
                <Text style={styles.body}>{post.body}</Text>
                <View style={styles.stats}>
                    <Text style={styles.stat}>👁️ {post.view_count} views</Text>
                    <Text style={styles.stat}>💬 {post.reply_count} replies</Text>
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
    meta: {
        fontSize: 12,
        color: Colors.secondary,
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
        marginBottom: 16,
    },
    stats: {
        flexDirection: 'row',
        gap: 16,
        paddingTop: 16,
        borderTopWidth: 1,
        borderTopColor: Colors.border,
    },
    stat: {
        fontSize: 14,
        color: Colors.secondary,
    },
    errorText: {
        color: Colors.primary,
        fontSize: 16,
    },
});
