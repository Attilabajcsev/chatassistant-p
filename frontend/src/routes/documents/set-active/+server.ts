// frontend/src/routes/documents/set-active/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

// POST handler for setting active documents
export async function POST(event: RequestEvent) {
  console.log("set active documents POST request received");
  const accessToken = event.cookies.get('accessToken');

  try {
    const body = await event.request.json();
    console.log("Request body:", body);

    const response = await fetch('http://127.0.0.1:8000/api/documents/set-active/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      console.error(`Set active documents API error: ${response.status}`);
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
    console.log('Set active documents API - Success');
    return json(data);
  } catch (error) {
    console.error('Set active documents API error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}