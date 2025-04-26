// frontend/src/lib/types.ts
export type AdminData = {
    backgrounds: BackgroundData[];
    activeBackground: BackgroundData | null;
    documents: Document[];
    activeDocument: string | null;
    prompt: Prompt;
    activePrompt: Prompt | null;
    settings: Settings;
    loading?: boolean;
    error?: string | null;
}

export type BackgroundData = {
    id: number;
    name: string;
    image_url: string;
    is_active: boolean;
    created_at?: string;
}

export type Prompt = {
    id: number;
    name: string;
    assistant_role: string;
    website_context: string;
    knowledge_context: string;
    response_guidelines: string;
    restrictions: string;
    is_active: boolean;
    created_at?: string;
}

export type Settings = {
    chatName: string;
    colorPrimary: string;
    buttonBg: string;
    welcomeMessage: string;
    disclaimerTitle: string;
    disclaimerIntro: string;
    disclaimerPoints: string[];
    acceptButtonText: string;
    sendButtonText: string;
    footerDisclaimer: string;
    privacyPolicyText: string;
}

export type Message = {
    role: string;
    text: string;
};

export type Document = {
    id: number;
    title: string;
    content: string;
    source: string;
    created_at: string;
    is_active: boolean;
}