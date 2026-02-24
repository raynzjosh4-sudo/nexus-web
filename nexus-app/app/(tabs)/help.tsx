import { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Colors from '@/constants/Colors';

interface FAQItem {
    question: string;
    answer: string;
}

interface FAQSection {
    category: string;
    items: FAQItem[];
}

const faqData: FAQSection[] = [
    {
        category: 'Getting Started',
        items: [
            {
                question: 'What is Nexus?',
                answer: 'Nexus is a community marketplace platform that connects people to swap items, find lost belongings, ask for recommendations, and discover local businesses.',
            },
            {
                question: 'How do I create an account?',
                answer: 'Download the Nexus app, click Sign Up, enter your email and create a password. Verify your email and you\'re ready to go!',
            },
        ],
    },
    {
        category: 'Swapping Items',
        items: [
            {
                question: 'How do I list an item for swap?',
                answer: 'Go to Swap section, click Create New Swap, add photos, title, description of what you have and what you\'re looking for.',
            },
            {
                question: 'Is swapping safe?',
                answer: 'Yes! Meet in public places, verify profiles, inspect items before swapping, and trust your instincts.',
            },
        ],
    },
    {
        category: 'Lost & Found',
        items: [
            {
                question: 'How do I report a lost item?',
                answer: 'Go to Lost & Found, click Report Lost Item, provide details like when/where you lost it, and add a photo if possible.',
            },
            {
                question: 'How can I claim a found item?',
                answer: 'If you see your lost item listed, click Claim This Item and verify ownership by describing specific details.',
            },
        ],
    },
];

export default function HelpScreen() {
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

    const toggleItem = (key: string) => {
        const newExpanded = new Set(expandedItems);
        if (newExpanded.has(key)) {
            newExpanded.delete(key);
        } else {
            newExpanded.add(key);
        }
        setExpandedItems(newExpanded);
    };

    const filteredData = faqData
        .map((section) => ({
            ...section,
            items: section.items.filter(
                (item) =>
                    !searchQuery ||
                    item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    item.answer.toLowerCase().includes(searchQuery.toLowerCase())
            ),
        }))
        .filter((section) => section.items.length > 0);

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Help & Support</Text>
                <Text style={styles.subtitle}>Find answers to common questions</Text>
            </View>

            <View style={styles.searchContainer}>
                <Ionicons name="search" size={18} color={Colors.primary} />
                <TextInput
                    style={styles.searchInput}
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    placeholder="Search help articles..."
                    placeholderTextColor={Colors.textMuted}
                />
            </View>

            {filteredData.map((section, sectionIndex) => (
                <View key={sectionIndex} style={styles.section}>
                    <Text style={styles.sectionTitle}>{section.category}</Text>
                    {section.items.map((item, itemIndex) => {
                        const key = `${sectionIndex}-${itemIndex}`;
                        const isExpanded = expandedItems.has(key);

                        return (
                            <TouchableOpacity
                                key={itemIndex}
                                style={styles.faqItem}
                                onPress={() => toggleItem(key)}
                            >
                                <View style={styles.questionRow}>
                                    <Text style={styles.question}>{item.question}</Text>
                                    <Ionicons
                                        name={isExpanded ? 'chevron-up' : 'chevron-down'}
                                        size={20}
                                        color={Colors.primary}
                                    />
                                </View>
                                {isExpanded && <Text style={styles.answer}>{item.answer}</Text>}
                            </TouchableOpacity>
                        );
                    })}
                </View>
            ))}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    header: {
        padding: 20,
        alignItems: 'center',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: Colors.secondary,
    },
    searchContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: Colors.header,
        borderRadius: 12,
        paddingHorizontal: 16,
        paddingVertical: 12,
        marginHorizontal: 16,
        marginBottom: 24,
        gap: 12,
    },
    searchInput: {
        flex: 1,
        color: Colors.text,
        fontSize: 15,
    },
    section: {
        marginBottom: 32,
        paddingHorizontal: 16,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: Colors.primary,
        marginBottom: 16,
        paddingBottom: 8,
        borderBottomWidth: 2,
        borderBottomColor: Colors.border,
    },
    faqItem: {
        backgroundColor: Colors.header,
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    questionRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    question: {
        flex: 1,
        fontSize: 16,
        fontWeight: '600',
        color: Colors.primary,
    },
    answer: {
        marginTop: 12,
        fontSize: 14,
        color: Colors.textSecondary,
        lineHeight: 20,
    },
});
