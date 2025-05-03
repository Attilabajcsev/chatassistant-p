import type { PageServerLoad } from './$types';
import type { AdminData } from '$lib/types';
import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL
const API_BASE = BACKEND_URL + '/api';

// Helper functions to fetch data from API
async function getBackgrounds(accessToken: string) {
  try {
    const response = await fetch(`${API_BASE}/backgrounds/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (!response.ok) {
      return { backgrounds: [], activeBackground: null };
    }
    
    const data = await response.json();
    const backgrounds = data.backgrounds || [];
    const activeBackground = backgrounds.find(bg => bg.is_active) || null;
    
    return { backgrounds, activeBackground };
  } catch (error) {
    console.error("Error fetching backgrounds:", error);
    return { backgrounds: [], activeBackground: null };
  }
}

async function getDocuments(accessToken: string) {
  try {
    const response = await fetch(`${API_BASE}/documents/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (!response.ok) {
      return { documents: [], activeDocument: null };
    }
    
    const data = await response.json();
    const documents = data.documents || [];
    
    let activeDocument = null;
    for (const doc of documents) {
      if (doc.is_active) {
        const sourceName = doc.source || "Unknown";
        activeDocument = sourceName.replace(/\s*-\s*Part\s*\d+$/i, "");
        break;
      }
    }
    
    return { documents, activeDocument };
  } catch (error) {
    console.error("Error fetching documents:", error);
    return { documents: [], activeDocument: null };
  }
}

async function getSettings(fetch: any) {
  try {
    const response = await fetch('/settings', {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!response.ok) {
      return {
        chatName: 'Chat Assistant',
        colorPrimary: '#4B5563',
        buttonBg: '#4B5563',
        disclaimerTitle: 'Welcome',
        disclaimerIntro: 'Please read the following information:',
        disclaimerPoints: [],
        welcomeMessage: "Welcome! How can I help you today?",
        acceptButtonText: "Accept",
        sendButtonText: "Send",
        footerDisclaimer: "This AI assistant provides information based on publicly available data.",
        privacyPolicyText: "Privacy Policy"
      };
    }
    
    const settings = await response.json();
    return settings;
  } catch (error) {
    console.error("Error fetching settings:", error);
    return {
      chatName: 'Chat Assistant',
      colorPrimary: '#4B5563',
      buttonBg: '#4B5563',
      disclaimerTitle: 'Welcome',
      disclaimerIntro: 'Please read the following information:',
      disclaimerPoints: [],
      welcomeMessage: "Welcome! How can I help you today?",
      acceptButtonText: "Accept",
      sendButtonText: "Send",
      footerDisclaimer: "This AI assistant provides information based on publicly available data.",
      privacyPolicyText: "Privacy Policy"
    };
  }
}

async function getPrompt(fetch: any) {
  try {
    const response = await fetch('/prompts', {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!response.ok) {
      return { 
        prompt: {
          name: "Default Assistant",
          assistant_role: "You are a helpful AI assistant answering questions based on the provided context.",
          website_context: "",
          knowledge_context: "",
          response_guidelines: "Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
          restrictions: "Only answer based on the provided context. Do not make up information."
        } 
      };
    }
    
    const data = await response.json();
    return { prompt: data.prompt || null };
  } catch (error) {
    console.error("Error fetching prompt:", error);
    return { 
      prompt: {
        name: "Default Assistant",
        assistant_role: "You are a helpful AI assistant answering questions based on the provided context.",
        website_context: "",
        knowledge_context: "",
        response_guidelines: "Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
        restrictions: "Only answer based on the provided context. Do not make up information."
      } 
    };
  }
}

export const load: PageServerLoad = async ({ locals, cookies, fetch }) => {
  
  const accessToken = cookies.get('accessToken');
  if (!accessToken) {
    console.log("Dashboard: No access token found, redirecting to login");
    throw redirect(303, '/login');
  }
  
  try {
    console.log("Dashboard: Fetching data for authenticated user");
    
    const [backgroundData, documentData, settingsData, promptData] = await Promise.all([
      getBackgrounds(accessToken),
      getDocuments(accessToken),
      getSettings(fetch),
      getPrompt(fetch)
    ]);
    
    
    const adminData: AdminData = {
      backgrounds: backgroundData.backgrounds,
      activeBackground: backgroundData.activeBackground,
      documents: documentData.documents,
      activeDocument: documentData.activeDocument,
      prompt: promptData.prompt || {
        name: "Default Assistant",
        assistant_role: "You are a helpful AI assistant answering questions based on the provided context.",
        website_context: "",
        knowledge_context: "",
        response_guidelines: "Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
        restrictions: "Only answer based on the provided context. Do not make up information."
      },
      activePrompt: null,
      settings: settingsData
    };
    
    return {
      adminData,
      userInfo: locals.authedUser
    };
  } catch (error) {
    console.error("Error loading admin data:", error);

    return {
      adminData: {
        backgrounds: [],
        activeBackground: null,
        documents: [],
        activeDocument: null,
        prompt: {
          name: "Default Assistant",
          assistant_role: "You are a helpful AI assistant answering questions based on the provided context.",
          website_context: "",
          knowledge_context: "",
          response_guidelines: "Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
          restrictions: "Only answer based on the provided context. Do not make up information."
        },
        activePrompt: null,
        settings: {
          chatName: 'Chat Assistant',
          colorPrimary: '#4B5563',
          buttonBg: '#4B5563',
          disclaimerTitle: 'Welcome',
          disclaimerIntro: 'Please read the following information:',
          disclaimerPoints: [],
          welcomeMessage: "Welcome! How can I help you today?",
          acceptButtonText: "Accept",
          sendButtonText: "Send",
          footerDisclaimer: "This AI assistant provides information based on publicly available data.",
          privacyPolicyText: "Privacy Policy"
        }
      },
      userInfo: locals.authedUser
    };
  }
};