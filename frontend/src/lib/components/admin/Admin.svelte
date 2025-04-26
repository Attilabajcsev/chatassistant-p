<script lang="ts">
    import BackgroundManager from "./BackgroundManager.svelte";
    import DocumentManager from "./DocumentManager.svelte";
    import ChatSettingsManager from "./ChatSettingsManager.svelte";
    import PromptManager from "./PromptManager.svelte";

    let {showAdmin}: {showAdmin:boolean} = $props();
    let adminTab: string = $state("backgrounds");
</script>

{#if showAdmin}
    <div class="absolute top-16 left-4 w-[675px] z-20">
        <div class="bg-white rounded-lg shadow-md mb-2">
            <div class="flex border-b">
                <button 
                    class:border-[#6256CA]={adminTab === "backgrounds"} 
                    class:border-b-2={adminTab === "backgrounds"} 
                    class:text-[#6256CA]={adminTab === "backgrounds"} 
                    class="flex-1 py-3 text-center font-medium transition-colors hover:bg-gray-50" 
                    onclick={() => adminTab = "backgrounds"}
                > 
                    Backgrounds 
                </button>
                <button 
                    class:border-[#6256CA]={adminTab === "documents"} 
                    class:border-b-2={adminTab === "documents"} 
                    class:text-[#6256CA]={adminTab === "documents"} 
                    class="flex-1 py-3 text-center font-medium transition-colors hover:bg-gray-50" 
                    onclick={() => adminTab = "documents"}
                > 
                    Documents 
                </button>
                <button 
                    class:border-[#6256CA]={adminTab === "settings"} 
                    class:border-b-2={adminTab === "settings"} 
                    class:text-[#6256CA]={adminTab === "settings"} 
                    class="flex-1 py-3 text-center font-medium transition-colors hover:bg-gray-50" 
                    onclick={() => adminTab = "settings"}
                > 
                    Settings 
                </button>
                <button 
                    class:border-[#6256CA]={adminTab === "prompt"} 
                    class:border-b-2={adminTab === "prompt"} 
                    class:text-[#6256CA]={adminTab === "prompt"} 
                    class="flex-1 py-3 text-center font-medium transition-colors hover:bg-gray-50" 
                    onclick={() => adminTab = "prompt"}
                > 
                    Prompt 
                </button>
            </div>
        </div>
        {#if adminTab === "backgrounds"} 
            <BackgroundManager />
        {:else if adminTab === "documents"} 
            <DocumentManager />
        {:else if adminTab === "settings"} 
            <ChatSettingsManager />
        {:else if adminTab === "prompt"} 
            <PromptManager />
        {/if}
    </div>
{/if}

<style>
    /* Ensure consistent tab styling */
    button.border-\[\#6256CA\] {
        border-color: #6256CA !important;
    }
    
    button.text-\[\#6256CA\] {
        color: #6256CA !important;
    }
</style>