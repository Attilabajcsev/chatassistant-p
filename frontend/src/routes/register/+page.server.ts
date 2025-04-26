import { redirect } from '@sveltejs/kit';

export async function load({locals, cookies}){

    // Logic that redirects user to the landing page if authenticated
    if(locals.authedUser){
        console.log("Register server: user found, redirect to landing")
        redirect(303, '/landing');
    }

    const accessToken = cookies.get('accessToken');
    return {accessToken}
}