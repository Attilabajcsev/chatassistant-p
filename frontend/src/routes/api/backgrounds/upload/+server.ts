// frontend/src/routes/api/backgrounds/upload/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function POST(event: RequestEvent) {

  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Background upload - No access token found in cookies or headers');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {

    const formData = await event.request.formData();
        
    const file = formData.get('background_image');
    if (file instanceof File) {
      console.log('Background upload - File details:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
    }
        
    const headers = new Headers();
    headers.set('Authorization', `Bearer ${accessToken}`);
  
    const response = await fetch('http://127.0.0.1:8000/api/backgrounds/upload/', {
      method: 'POST',
      headers,
      body: formData
    });
    
    console.log('Background upload - Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Background upload - Error response body:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status} - ${errorText}`
      }, { status: response.status });
    }
    
    const data = await response.json();
    console.log('Background upload - Success response:', data);
    
    return json(data);
  } catch (error) {
    console.error('Background upload - Error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}`
    }, { status: 500 });
  }
}