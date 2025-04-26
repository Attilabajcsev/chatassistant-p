<script lang="ts">

  let email = $state('');
  let password = $state('');
  let errorMessage = $state('');
  let isLoading = $state(false);

  async function handleSignUp() {

      if (!email || !password) {
          errorMessage = 'Please enter both email and password';
          return;
      }

      isLoading = true;
      errorMessage = '';
      console.log(email)
      console.log(password)
      try {
          const response = await fetch('http://127.0.0.1:8000/api/user/register/', {
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

          if (response) {
              const data = await response.json();
              console.log(data)
          } else {
              errorMessage = 'Sign up failed. Please try again.';
          }
      } catch (error) {
          console.error('Login error:', error);
          errorMessage = 'An error occurred. Please try again.';
      } finally {
          isLoading = false;
      }
  }

  // --- Icons (Inline SVG examples) ---
  const mailIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" /></svg>`;
  const lockIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>`;

  // --- Define Colors ---
  const purpleColor = '#6256CA';
  const greenColor = '#00FF9C';
</script>

<div class="relative min-h-screen flex items-center justify-center bg-white p-6 overflow-hidden">

  <div class="absolute -top-4 -left-16 w-96 h-96 md:w-[480px] md:h-[480px] lg:w-[576px] lg:h-[576px] opacity-90 pointer-events-none z-0">
      <img
          src="/greenwave.svg"  alt="Decorative green wave element"
          class="w-full h-full object-contain"
      />
  </div>


  <div class="w-full max-w-sm z-10">

      <h1 class="text-3xl font-semibold text-center mb-8" style:color={purpleColor}>Sign up</h1>

      {#if errorMessage}
          <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 text-sm" role="alert">
              {errorMessage}
          </div>
      {/if}

      <form onsubmit={handleSignUp} class="space-y-5">
          <div class="relative flex items-center bg-white border border-gray-300 rounded-md px-3 py-1.5 shadow-sm focus-within:ring-1 focus-within:ring-[#6256CA] focus-within:border-[#6256CA]">
               <span class="text-[#6256CA] pr-2">{@html mailIconSvg}</span>
              <input
                  type="email"
                  bind:value={email}
                  class="w-full p-1.5 bg-transparent border-none focus:outline-none placeholder-gray-400 text-sm"
                  placeholder="admin@example.com"
                  required
                  disabled={isLoading}
              />
          </div>

          <div class="relative flex items-center bg-white border border-gray-300 rounded-md px-3 py-1.5 shadow-sm focus-within:ring-1 focus-within:ring-[#6256CA] focus-within:border-[#6256CA]">
               <span class="text-[#6256CA] pr-2">{@html lockIconSvg}</span>
              <input
                  type="password"
                  bind:value={password}
                  class="w-full p-1.5 bg-transparent border-none focus:outline-none placeholder-gray-400 text-sm"
                  placeholder="••••••••••"
                  required
                  disabled={isLoading}
              />
          </div>

          <div class="text-right pr-1">
              <a href="/login" class="text-xs hover:underline" style:color={greenColor}>
                  Already have an account?
              </a>
          </div>

          <div class="pt-3">
              <button
                  type="submit"
                  class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#6256CA] hover:opacity-90 transition duration-150 ease-in-out"
                  style:background-color={purpleColor}
                  disabled={isLoading}
              >
                  {#if isLoading}
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"> <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle> <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path> </svg>
                      Signing up...
                  {:else}
                      Sign up
                  {/if}
              </button>
          </div>
      </form>
  </div>

   <div class="absolute bottom-4 right-6 md:bottom-20 md:right-20 z-10">
       <img
          src="/logo.svg" alt="Company Logo"
          class="h-20 w-auto" />
   </div>

</div>