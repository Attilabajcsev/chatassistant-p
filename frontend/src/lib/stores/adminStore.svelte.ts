import type { AdminData, Prompt } from '../types';

export const adminStore: AdminData = $state({
    backgrounds: [],
    activeBackground: null,
    documents: [],
    activeDocument: null,
    prompt: {} as Prompt,
    activePrompt: null,
    settings: {
        chatName: 'Loading...',
        colorPrimary: '#4B5563',
        buttonBg: '#4B5563',
        disclaimerTitle: 'Welcome',
        disclaimerIntro: 'Please read the following information',
        disclaimerPoints: [],
        welcomeMessage: "Welcome! How can I help you today?",
        acceptButtonText: "Accept",
        sendButtonText: "Send",
        footerDisclaimer: "This AI assistant provides information based on publicly available data.",
        privacyPolicyText: "Privacy Policy"
    }
});
