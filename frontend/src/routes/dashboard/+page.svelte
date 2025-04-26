<script lang="ts">

    import Admin from "$lib/components/admin/Admin.svelte";
    import Chat from "$lib/components/chat/Chat.svelte";
    import type { AdminData } from "$lib/types";
    import { adminStore } from "$lib/stores/adminStore.svelte";
    import { goto } from "$app/navigation";
    
    // Get server-provided data
    let { data }: {data: {adminData: AdminData, userInfo: string}} = $props();
    let showAdmin = $state(false);

    adminStore.settings = data.adminData.settings
    adminStore.prompt = data.adminData.prompt
    adminStore.activeBackground = data.adminData.activeBackground
    adminStore.activeDocument = data.adminData.activeDocument
    adminStore.activePrompt = data.adminData.activePrompt
    adminStore.backgrounds = data.adminData.backgrounds
    adminStore.documents = data.adminData.documents


</script>

<div class="relative min-h-screen bg-gray-200" data-component="dashboard">
    <div class="absolute inset-0 overflow-y-auto z-0">
        {#if adminStore.activeBackground?.image_url}
            <img src={adminStore.activeBackground.image_url} alt="Website screenshot background" class="block w-full h-auto max-w-none"/>
        {/if}
    </div>

    <div class="fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-4 py-2 bg-white shadow-md">
        <button 
            class="px-6 py-2 rounded font-medium text-white transition-all hover:opacity-90"
            style="background-color: #6256CA;"
            onclick={() => showAdmin = !showAdmin}
            data-testid="toggle-admin-button"
        >
            {showAdmin ? 'Close Admin' : 'Admin'}
        </button>
        
        <button 
            class="px-6 py-2 rounded font-medium transition-all hover:opacity-90"
            style="background-color: #00FF9C; color: #6256CA;"
            onclick={() => goto('/logout')}
        >
            Logout
        </button>
    </div>

    <Admin {showAdmin} />
    <Chat />
</div>