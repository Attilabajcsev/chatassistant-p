// frontend/src/routes/backgrounds/[backgroundId]/delete/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL

export async function DELETE(event: RequestEvent) {
  const { backgroundId } = event.params;
  console.log(`Delete background request received for ID: ${backgroundId}`);
  
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Delete background - No access token found');
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

    console.log(`Deleting background ID: ${backgroundId}`);
    
    const response = await fetch(BACKEND_URL+ `/api/backgrounds/${backgroundId}/delete/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Delete background response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Delete background error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Delete background success:', data);
    
    return json({
      ...data,
      status: 'success',
      message: 'Background deleted successfully'
    });
  } catch (error) {
    console.error('Delete background error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}