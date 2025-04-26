// src/routes/api/chat/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function POST(event: RequestEvent) {
  console.log("request recieved")
  const accessToken = event.cookies.get('accessToken');

  try {
    const body = await event.request.json();
    console.log(body)
        
    const response = await fetch('http://127.0.0.1:8000/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      console.error(`Chat API proxy - Backend returned error: ${response.status}`);
      const errorText = await response.text();
      
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        errorData = { detail: errorText || 'Unknown error' };
      }
      
      return json({ 
        status: 'error',
        message: errorData.detail || `Error ${response.status} from backend` 
      }, { status: response.status });
    }
    
    const data = await response.json();
    console.log('Chat API proxy - Received successful response from backend');
    
    return json(data);
    
  } catch (error) {
    console.error('Chat API proxy - Error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}