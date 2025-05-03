// frontend/src/routes/documents/set-active/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL

export async function POST(event: RequestEvent) {
  console.log("Set active documents POST request received");
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Set active documents - No access token found');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    const body = await event.request.json();
    const documentIds = body.document_ids;
    
    console.log("Setting active document IDs:", documentIds);

    if (!Array.isArray(documentIds)) {
      return json({ 
        status: 'error',
        message: 'Invalid document_ids format - must be an array' 
      }, { status: 400 });
    }

    const response = await fetch(BACKEND_URL + '/api/documents/set-active/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ document_ids: documentIds })
    });

    console.log("Set active documents response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Set active documents error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Set active documents success:', data);
    
    return json({
      ...data,
      status: 'success',
      message: 'Documents set as active successfully'
    });
  } catch (error) {
    console.error('Set active documents error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}