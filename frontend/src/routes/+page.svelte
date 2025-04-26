<script lang="ts">
    import { goto } from "$app/navigation";

    const purpleColor = '#6256CA';

</script>
  
<div class="relative min-h-screen flex items-center justify-center bg-white p-6 overflow-hidden">

    <div class="absolute -top-4 -left-16 w-96 h-96 md:w-[480px] md:h-[480px] lg:w-[576px] lg:h-[576px] opacity-90 pointer-events-none z-0">
        <img
            src="/greenwave.svg"  alt="Decorative green wave element"
            class="w-full h-full object-contain"
        />
    </div>

    <div>
        <h1 class="font-semibold text-5xl p-4 mb-4">Welcome to converIQ!</h1>
        <button 
            class="mb-4 w-[50%] m-auto flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#6256CA] hover:opacity-90 transition duration-150 ease-in-out"
            style:background-color={purpleColor}
            type="button"
            onclick={() => goto('/register')}
        >Sign up</button>
        <button 
            class="w-[50%] m-auto flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#6256CA] hover:opacity-90 transition duration-150 ease-in-out"
            style:background-color={purpleColor}
            type="button"
            onclick={() => goto('/login')}
        >Login</button>
    </div>

    <div class="absolute bottom-4 right-6 md:bottom-20 md:right-20 z-10">
        <img
           src="/logo.svg" alt="Company Logo"
           class="h-20 w-auto" />
    </div>
</div>
  