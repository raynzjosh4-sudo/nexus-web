# Nexus React Native App

A React Native mobile app built with Expo for the Nexus community platform.

## Features

- Community posts feed with search and filtering
- Lost & Found items listing
- Help & FAQ section
- Dark theme matching the web design
- Supabase integration for real-time data

## Setup

1. Install dependencies:
```bash
cd nexus-app
npm install
```

2. Start the development server:
```bash
npm start
```

3. Run on your device:
- Press `a` for Android
- Press `i` for iOS
- Scan QR code with Expo Go app

## Project Structure

```
nexus-app/
├── app/                    # Expo Router screens
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── index.tsx      # Community feed
│   │   ├── lost-found.tsx # Lost & Found
│   │   └── help.tsx       # FAQ
│   ├── community/[id].tsx # Post details
│   └── lost-found/[id].tsx # Item details
├── components/            # Reusable components
├── services/             # API and Supabase
└── constants/            # Theme colors
```

## Technologies

- React Native
- Expo Router (file-based routing)
- TypeScript
- Supabase (backend)
- Expo Vector Icons

## Build for Production

```bash
# Android
npm run android

# iOS
npm run ios
```
