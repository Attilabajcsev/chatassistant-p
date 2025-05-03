// frontend/src/routes/documents/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL

// GET handler for listing all documents
export async function GET(event: RequestEvent) {
  console.log("Documents GET request received");
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Document list - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    console.log("Fetching documents from backend...");
    
    // Direct request to the backend
    const response = await fetch(BACKEND_URL + '/api/documents/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Documents response status:", response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Documents error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    // Directly parse and return the JSON response, matching the pattern used by other endpoints
    const data = await response.json();
    console.log('Documents success - document count:', data.documents?.length || 0);
    
    return json(data);
  } catch (error) {
    console.error('Documents API error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}