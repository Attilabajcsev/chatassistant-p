import type {Actions,RequestEvent,ActionFailure,Redirect} from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL
const LOGIN_URL = BACKEND_URL + '/api/token/';


export async function load({locals, cookies}){

    // Logic that redirects user to the landing page if authenticated
    if(locals.authedUser){
        console.log("Login server: user found, redirect to landing")
        redirect(303, '/dashboard');
    }

    const accessToken = cookies.get('accessToken');
    return {accessToken}
}

export const actions:Actions = {
    login: async ({cookies,request}:RequestEvent) =>{

        const loginFormData = await request.formData();
        const email = loginFormData.get('email')?.toString()?? '';
        const password = loginFormData.get('password')?.toString()?? '';

        let loginResponse = {
            email,
            error: false,
            message: ''
        }


        const response = await fetch(LOGIN_URL, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                {
                    username: email,
                    password: password
                }
            )
        });

        if (response.ok) {
            const data = await response.json();
            const accessToken = data.access;
            const refreshToken = data.refresh;

            cookies.set('accessToken',accessToken,{httpOnly: true, path:"/", maxAge: 60 * 60 ,sameSite: 'strict'}); //expires in 1h
            cookies.set('refreshToken',refreshToken,{httpOnly: true, path:"/", maxAge: 60 * 60 * 24 * 7,sameSite: 'strict'}) // expires in 1 week
            console.log('login successful. Redirecting..')
            redirect(303, '/dashboard')

        } else {
            loginResponse.message = 'Sign up failed. Please try again.';
            loginResponse.error = true;
            return loginResponse

        }
    }
}