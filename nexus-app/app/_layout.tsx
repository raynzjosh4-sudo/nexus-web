import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
    return (
        <>
            <StatusBar style="light" />
            <Stack
                screenOptions={{
                    headerStyle: { backgroundColor: '#1a0f2e' },
                    headerTintColor: '#a855f7',
                    headerTitleStyle: { fontWeight: 'bold' },
                    contentStyle: { backgroundColor: '#000000' },
                }}
            >
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="community/[id]" options={{ title: 'Post Details' }} />
                <Stack.Screen name="lost-found/[id]" options={{ title: 'Item Details' }} />
            </Stack>
        </>
    );
}
