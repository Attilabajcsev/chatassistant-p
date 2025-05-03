import { redirect } from '@sveltejs/kit';
import { jwtDecode } from 'jwt-decode';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL
const VERIFY_URL = BACKEND_URL + '/api/token/verify/';
const REFRESH_URL = BACKEND_URL + '/api/token/refresh/';



function clearCookies(event): void {
	event.cookies.delete("accessToken", { path: "/" });
	event.cookies.delete("refreshToken", { path: "/" });
}

export async function handle({ event, resolve }) {
	console.log("Hook: Checking token validity for each server request");
	let accessToken = event.cookies.get("accessToken");
	const refreshToken = event.cookies.get("refreshToken");

	if (accessToken) {
		const verifyResponse = await fetch(VERIFY_URL, {
			method: "POST",
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ token: accessToken })
		});

		if (verifyResponse.ok) {
			const decoded: any = jwtDecode(accessToken);
			event.locals.authedUser = decoded.user_id;

		} else if (refreshToken) {
			const refreshResponse = await fetch(REFRESH_URL, {
				method: "POST",
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh: refreshToken })
			});

			if (refreshResponse.ok) {
				const { access } = await refreshResponse.json();
				event.cookies.set('accessToken', access, {
					httpOnly: true,
					path: "/",
					maxAge: 60 * 60,
					sameSite: 'strict'
				});
				const decoded: any = jwtDecode(access);
				event.locals.authedUser = decoded.user_id;
				accessToken = access;
			} else {
				clearCookies(event);
			}
		} else {
			clearCookies(event);
		}
	} else {
		clearCookies(event);
	}

	// Protect routes that require authentication
	const publicRoutes = ['/', '/login', '/register'];
	const isPublicRoute = publicRoutes.includes(event.url.pathname);

	if (!isPublicRoute && !event.locals.authedUser) {
		console.log(`Hook: Unauthorized access attempt to ${event.url.pathname}`);
		throw redirect(302, '/');
	}

	if (event.locals.authedUser) {
		console.log(`Hook: Current user id authenticated: ${event.locals.authedUser}`);
	} else {
		console.log("Hook: No user found");
	}

	const response = await resolve(event);
	return response;
}