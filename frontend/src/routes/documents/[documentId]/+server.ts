// frontend/src/routes/documents/[documentId]/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL

// DELETE handler for removing documents
export async function DELETE(event: RequestEvent) {
  console.log("Documents DELETE request received");
  const accessToken = event.cookies.get('accessToken');
  const { documentId } = event.params;

  if (!accessToken) {
    console.error('Document delete - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    if (!documentId || isNaN(parseInt(documentId))) {
      return json({ 
        status: 'error',
        message: 'Invalid document ID' 
      }, { status: 400 });
    }

    console.log(`Deleting document with ID: ${documentId}`);
    
    const response = await fetch(BACKEND_URL + `/api/documents/${documentId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Document delete response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Document delete error response:', errorText);
      
      return json({ 
        status: 'error',
        message: `Backend returned error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Document delete success');
    
    return json({
      ...data,
      status: 'success'
    });
  } catch (error) {
    console.error('Document delete error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}