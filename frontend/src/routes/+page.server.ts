import { redirect } from '@sveltejs/kit';

export async function load({locals}){

    let authedUser = undefined

    // Logic that redirects user to the landing page if authenticated
    if(locals.authedUser){
        authedUser = locals.authedUser;
        console.log("Main server: user found, redirect to landing")
        redirect(303, '/dashboard');
    }

    return{authedUser}
}