import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function GET(event: RequestEvent) {
  console.log("settings GET request received")
  const accessToken = event.cookies.get('accessToken');

  try {
    const response = await fetch('http://127.0.0.1:8000/api/settings/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (!response.ok) {
      console.error(`Settings API proxy - Backend returned error: ${response.status}`);
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
    console.log('Settings API proxy - Received successful response from backend');
    
    return json(data);
    
  } catch (error) {
    console.error('Settings API proxy - Error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}

export async function POST(event: RequestEvent) {
  console.log("settings POST request received")
  const accessToken = event.cookies.get('accessToken');

  try {
    const body = await event.request.json();
    console.log(body)
        
    const response = await fetch('http://127.0.0.1:8000/api/settings/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      console.error(`Settings API proxy - Backend returned error: ${response.status}`);
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
    console.log('Settings API proxy - Received successful response from backend');
    
    return json(data);
    
  } catch (error) {
    console.error('Settings API proxy - Error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}