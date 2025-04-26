// frontend/src/routes/backgrounds/[backgroundId]/set-active/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function POST(event: RequestEvent) {
  const { backgroundId } = event.params;
  console.log(`Set active background POST request received for ID: ${backgroundId}`);
  
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Set active background - No access token found');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    if (!backgroundId || isNaN(parseInt(backgroundId))) {
      return json({ 
        status: 'error',
        message: 'Invalid background ID' 
      }, { status: 400 });
    }

    console.log(`Setting background ID ${backgroundId} as active`);
    
    const response = await fetch(`http://127.0.0.1:8000/api/backgrounds/${backgroundId}/set-active/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Set active background response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Set active background error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Set active background success:', data);
    
    return json({
      ...data,
      status: 'success',
      message: 'Background set as active successfully'
    });
  } catch (error) {
    console.error('Set active background error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}