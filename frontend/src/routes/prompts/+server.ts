// frontend/src/routes/prompts/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function GET(event: RequestEvent) {
  console.log("prompts GET request received");
  const accessToken = event.cookies.get('accessToken');

  try {
    const response = await fetch('http://127.0.0.1:8000/api/prompts/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) {
      console.error(`Prompts API error: ${response.status}`);
      return json({ 
        status: 'error',
        message: `Error ${response.status} from backend` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Prompts API - Success');
    return json(data);

  } catch (error) {
    console.error('Prompts API error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}

export async function POST(event: RequestEvent) {
  console.log("update prompt POST request received");
  const accessToken = event.cookies.get('accessToken');

  try {
    const body = await event.request.json();
    console.log("Request body:", body);

    const response = await fetch('http://127.0.0.1:8000/api/prompts/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      console.error(`Update prompt API error: ${response.status}`);
      return json({ 
        status: 'error',
        message: `Error ${response.status} from backend` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Update prompt API - Success');
    return json(data);
  } catch (error) {
    console.error('Update prompt API error:', error);
    return json({ 
      status: 'error',
      message: 'Internal server error' 
    }, { status: 500 });
  }
}