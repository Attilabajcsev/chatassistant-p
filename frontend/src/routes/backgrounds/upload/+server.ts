// frontend/src/routes/backgrounds/upload/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function POST(event: RequestEvent) {
  console.log("Background upload request received at /backgrounds/upload/");
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Background upload - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    const formData = await event.request.formData();
    console.log('Background upload - FormData fields:', Array.from(formData.keys()));
        
    const file = formData.get('background_image');
    if (file instanceof File) {
      console.log('Background upload - File details:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
    } else {
      console.error('Background upload - No file or invalid file in request');
      return json({ 
        status: 'error',
        message: 'No valid file found in the request' 
      }, { status: 400 });
    }
        
    // Make sure we're setting the authorization header correctly
    const headers = new Headers();
    headers.set('Authorization', `Bearer ${accessToken}`);
  
    console.log('Background upload - Forwarding to backend API with token');
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
    
    return json({
      ...data,
      status: 'success',
      message: 'Background image uploaded successfully'
    });
  } catch (error) {
    console.error('Background upload - Error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}`
    }, { status: 500 });
  }
}