// frontend/src/routes/documents/[documentId]/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

// DELETE handler for removing documents
export async function DELETE(event: RequestEvent) {
  console.log("documents DELETE request received");
  const accessToken = event.cookies.get('accessToken');
  const { documentId } = event.params;

  try {
    if (!documentId || isNaN(parseInt(documentId))) {
      return json({ 
        status: 'error',
        message: 'Invalid document ID' 
      }, { status: 400 });
    }

    const response = await fetch(`http://127.0.0.1:8000/api/documents/${documentId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) {
      console.error(`Delete document API error: ${response.status}`);
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
    console.log('Delete document API - Success');
    return json(data);
  } catch (error) {
    console.error('Delete document API error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}