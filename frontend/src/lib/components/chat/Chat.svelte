<script lang="ts">
    import ChatWindow from "./ChatWindow.svelte";
    import Header from "./Header.svelte";
    import { adminStore } from "$lib/stores/adminStore.svelte";

    let show = $state(false);

    let settings = $derived(adminStore.settings);
</script>

<div class="fixed bottom-8 right-8 z-50">
    {#if !show}
        <button class="flex items-center shadow-lg rounded-xl pl-4 pr-3 py-2 chat-button-container" style="background-color: var(--color-primary); color: var(--color-white);" onclick={() => show = true}>
            <span class="text-sm mr-2 whitespace-nowrap">{settings.chatName}</span>
            <div class="flex items-center justify-center w-10 h-10 rounded-full bg-white ml-1">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-primary);">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            </div>
        </button>
    {:else}
        <div class="chat-window-container w-[400px] min-h-[600] flex flex-col rounded-xl shadow-2xl overflow-hidden" style="background-color: var(--bg-light); border: 1px solid var(--border-light); border-top: 4px solid var(--color-primary);">
            
            <Header bind:show chatName={settings.chatName}></Header>
            
            <ChatWindow placeholder="Miben segíthetek?" {settings}></ChatWindow>
            
            <div class="p-3 text-xs text-center" style="background-color: var(--bg-card); color: var(--text-dark);">
                {settings.footerDisclaimer}
                <br>
                <button type="button" class="underline">{settings.privacyPolicyText}</button>
            </div>
        </div>
    {/if}
</div>