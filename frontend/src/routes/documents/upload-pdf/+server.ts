// frontend/src/routes/documents/upload-pdf/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function POST(event: RequestEvent) {  
  console.log("Document upload request received");
  const accessToken = event.cookies.get('accessToken');
  
  if (!accessToken) {
    console.error('Document upload - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    const formData = await event.request.formData();
    console.log('Document upload - FormData fields:', Array.from(formData.keys()));

    const file = formData.get('pdf_file');
    if (file instanceof File) {
      console.log('Document upload - File details:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
    } else {
      console.error('Document upload - No file or invalid file in request');
      return json({ 
        status: 'error',
        message: 'No valid file found in the request' 
      }, { status: 400 });
    }

    const headers = new Headers();
    headers.set('Authorization', `Bearer ${accessToken}`);

    console.log('Document upload - Sending to backend');
    const response = await fetch('http://127.0.0.1:8000/api/documents/upload-pdf/', {
      method: 'POST',
      headers,
      body: formData
    });
    
    console.log('Document upload - Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Document upload - Error response body:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status} - ${errorText}`
      }, { status: response.status });
    }
    
    const data = await response.json();
    console.log('Document upload - Success response:', data);
    
    return json({
      ...data,
      status: 'success',
      message: `PDF processed successfully into ${data.document_count} chunks`
    });
  } catch (error) {
    console.error('Document upload - Error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}`
    }, { status: 500 });
  }
}