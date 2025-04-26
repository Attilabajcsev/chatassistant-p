// src/lib/sendMessage.ts
import type { Message } from "./types";

// Create API utility for authenticated requests
async function apiRequest(path: string, options: RequestInit = {}) {
  const url = `/api/${path}`;
  
  const defaultOptions: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    credentials: 'same-origin', // Important for cookies
  };
  
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };
  
  try {
    const response = await fetch(url, mergedOptions);
    
    if (!response.ok) {
      // Try to parse error response
      try {
        const errorData = await response.json();
        throw new Error(errorData.message || `API error: ${response.status}`);
      } catch (e) {
        throw new Error(`API error: ${response.status}`);
      }
    }
    
    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    console.error(`API request failed for ${path}:`, error);
    throw error;
  }
}

let conversationId: string | null = null;

export async function sendMessage(message: string, messages: Message[]) {
  // Push user message immediately
  messages.push({
    role: "user",
    text: message
  });
  
  // Set loading state (assuming these are reactive)
  let loading = true;
  
  try {
    console.log("Sending message to API:", message);
    
    // THIS IS THE KEY CHANGE - using our proxy API endpoint
    const response = await apiRequest('chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId
      })
    });
    
    console.log("API response:", response);
    
    if (response.status === 'success') {
      // Save conversation ID for subsequent messages
      if (response.conversation_id) {
        conversationId = response.conversation_id;
      }
      
      // Add AI response to messages
      messages.push({
        role: "agent",
        text: response.response
      });
    } else {
      // Handle error
      messages.push({
        role: "agent",
        text: "I'm sorry, I couldn't process your request. Please try again later."
      });
      console.error("API error:", response);
    }
  } catch (error) {
    console.error("Error sending message:", error);
    
    // Add error message
    messages.push({
      role: "agent",
      text: "I'm sorry, an error occurred while processing your message. Please try again."
    });
  } finally {
    // Reset loading state
    loading = false;
  }
}