<script lang="ts">
    import ChatWindow from "./ChatWindow.svelte";
    import Header from "./Header.svelte";
    import { adminStore } from "$lib/stores/adminStore.svelte";
    import { onMount } from "svelte";

    let show = $state(false);
    let settings = $derived(adminStore.settings);

    $effect(() => {
        updateCSSVariables(settings);
    });
    

    onMount(() => {
        updateCSSVariables(settings);
    });
    

    function updateCSSVariables(settings) {
        if (!settings) return;

        const root = document.documentElement;
        

        root.style.setProperty('--color-primary', settings.colorPrimary);
        root.style.setProperty('--chat-primary-color', settings.colorPrimary);
        root.style.setProperty('--chat-primary', settings.colorPrimary);
        root.style.setProperty('--chat-action-button', settings.buttonBg);
        root.style.setProperty('--chat-button-bg', settings.buttonBg);
        
        const primaryHover = darkenColor(settings.colorPrimary, 0.15);
        const buttonHover = darkenColor(settings.buttonBg, 0.15);
        
        root.style.setProperty('--chat-primary-light', primaryHover);
        root.style.setProperty('--chat-button-hover', buttonHover);
        root.style.setProperty('--button-bg-hover', buttonHover);
    }
    

    function darkenColor(color, amount) {
        try {

            let r = parseInt(color.substring(1, 3), 16);
            let g = parseInt(color.substring(3, 5), 16);
            let b = parseInt(color.substring(5, 7), 16);

            r = Math.max(0, Math.floor(r * (1 - amount)));
            g = Math.max(0, Math.floor(g * (1 - amount)));
            b = Math.max(0, Math.floor(b * (1 - amount)));

            return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
        } catch (e) {
            console.error("Error darkening color:", e);
            return color;
        }
    }
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
        <div class="chat-window-container flex flex-col rounded-xl shadow-2xl overflow-hidden" 
             style="background-color: var(--bg-light); border: 1px solid var(--border-light); border-top: 4px solid var(--color-primary);">
            
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

<style>
    /* Optional scrollbar styles */
    .overflow-y-auto::-webkit-scrollbar { width: 6px; }
    .overflow-y-auto::-webkit-scrollbar-track { background: transparent; }
    .overflow-y-auto::-webkit-scrollbar-thumb { background-color: var(--border-light); border-radius: 3px; }
    

    .chat-window-container {

        width: 15vw;
        height: 60vh;
        
        min-width: 300px;
        min-height: 400px;
        
        max-width: 500px;
        max-height: 80vh;
        
        transition: width 0.3s, height 0.3s;
    }
    
    .chat-button-container:hover {
        filter: brightness(0.9);
    }
</style>