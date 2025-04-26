// Modified frontend/src/routes/documents/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

// GET handler for listing all documents
export async function GET(event: RequestEvent) {
  console.log("Documents direct GET request received");
  const accessToken = event.cookies.get('accessToken');

  if (!accessToken) {
    console.error('Document list - No access token found in cookies');
    return json({ 
      status: 'error',
      message: 'Not authenticated' 
    }, { status: 401 });
  }

  try {
    console.log("Directly fetching documents from backend...");
    // Direct request to the backend to bypass any potential middleware issues
    const response = await fetch('http://127.0.0.1:8000/api/documents/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    console.log("Documents direct response status:", response.status);
    
    // Log response headers for debugging
    const headers = {};
    response.headers.forEach((value, key) => {
      headers[key] = value;
    });
    console.log("Response headers:", headers);

    if (!response.ok) {
      let errorMessage = `Error ${response.status}`;
      try {
        const errorText = await response.text();
        console.error('Documents direct error response:', errorText);
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.message || errorData.detail || errorMessage;
        } catch (e) {
          errorMessage = errorText || errorMessage;
        }
      } catch (e) {
        console.error('Failed to parse error response:', e);
      }
      
      return json({ 
        status: 'error',
        message: errorMessage
      }, { status: response.status });
    }

    // Log the raw response text for debugging
    const rawText = await response.text();
    console.log('Documents direct raw response:', rawText);
    
    let data;
    try {
      // Try to parse as JSON
      data = JSON.parse(rawText);
    } catch (e) {
      console.error('Failed to parse response as JSON:', e);
      return json({ 
        status: 'error',
        message: 'Invalid response format from backend' 
      }, { status: 500 });
    }
    
    // If the backend doesn't return a documents array, create an empty one
    if (!data.documents) {
      console.warn('Backend response is missing documents array, returning empty array');
      data.documents = [];
    }
    
    console.log('Documents direct success - document count:', data.documents.length);
    
    return json(data);
  } catch (error) {
    console.error('Documents direct API error:', error);
    return json({ 
      status: 'error',
      message: `Internal server error: ${error.message}` 
    }, { status: 500 });
  }
}