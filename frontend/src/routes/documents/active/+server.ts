// frontend/src/routes/documents/active/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL

// GET handler for listing active documents
export async function GET(event: RequestEvent) {
  console.log("active documents GET request received");
  const accessToken = event.cookies.get('accessToken');

  try {
    const response = await fetch(BACKEND_URL + '/api/documents/active/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) {
      console.error(`Active documents API error: ${response.status}`);
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
    console.log('Active documents API - Success');
    return json(data);

  } catch (error) {
    console.error('Active documents API error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}