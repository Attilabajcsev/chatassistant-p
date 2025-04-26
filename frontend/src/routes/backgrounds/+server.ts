// frontend/src/routes/backgrounds/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function GET(event: RequestEvent) {
  console.log("Backgrounds GET request received");
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Backgrounds list - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    console.log("Fetching backgrounds from backend...");
    
    const response = await fetch('http://127.0.0.1:8000/api/backgrounds/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Backgrounds response status:", response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backgrounds error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Backgrounds success - count:', data.backgrounds?.length || 0);
    
    return json(data);
  } catch (error) {
    console.error('Backgrounds API error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}