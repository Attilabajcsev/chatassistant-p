<script lang="ts">
    import DropZone from "$lib/components/ui/DropZone.svelte";
    import { adminStore } from "$lib/stores/adminStore.svelte"
    import { backgroundsApi } from "$lib/api/index"
    
    let error = $state("");
    let success = $state("");
    let showBackgroundList = $state(false);
    let showDeleteConfirm = $state(false);
    let backgroundToDelete = $state<number | null>(null);
    
    
    async function setActiveBackground(backgroundId: number) {
        try {
            await backgroundsApi.setActiveBackgroundAPI(backgroundId);
            success = "Background set as active successfully";
            error = "";

        } catch (err) {
            error = "Failed to set active background. Please try again.";
            success = "";
        }
    }
    
    
    function confirmDelete(backgroundId: number) {
        backgroundToDelete = backgroundId;
        showDeleteConfirm = true;
    }
    
    async function deleteBackground() {
        if (backgroundToDelete === null) return;
        
        try {
            await backgroundsApi.deleteBackgroundAPI(backgroundToDelete);
            success = "Background deleted successfully";
            error = "";
            showDeleteConfirm = false;
            backgroundToDelete = null;
        } catch (err) {
            error = "Failed to delete background. Please try again.";
            success = "";
            showDeleteConfirm = false;
        }
    }
    
    function cancelDelete() {
        showDeleteConfirm = false;
        backgroundToDelete = null;
    }
    
    function handleUploadSuccess(data: any) {
        success = "Background uploaded successfully!";
        error = "";
        
        backgroundsApi.getBackgrounds().then(() => {
            if (adminStore.backgrounds.length === 1) {
                const newBg = adminStore.backgrounds[0];
                if (newBg && newBg.id) {
                    setActiveBackground(newBg.id);
                }
            } else if (data && data.background_id) {
                setActiveBackground(data.background_id);
            }

        });
    }
    
    function handleUploadError(err: any) {
        error = "Failed to upload background. Please try again.";
        success = "";
    }

    
    function handleKeyDown(e: KeyboardEvent, backgroundId: number) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setActiveBackground(backgroundId);
        }
    }
</script>

<div class="p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-xl font-semibold mb-4">Background Image Manager</h2>
    
    {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
        </div>
    {/if}
    
    {#if success}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
        </div>
    {/if}
    
    <!-- Delete confirmation modal -->
    {#if showDeleteConfirm}
        <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div class="bg-white p-6 rounded-lg shadow-lg max-w-md">
                <h3 class="text-lg font-semibold mb-4">Confirm Deletion</h3>
                <p class="mb-6">Are you sure you want to delete this background image? This action cannot be undone.</p>
                <div class="flex justify-end space-x-4">
                    <button 
                        class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                        onclick={cancelDelete}
                    >
                        Cancel
                    </button>
                    <button 
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                        onclick={deleteBackground}
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    {/if}
    
    <DropZone 
        title="Drag & Drop Background Image" 
        subtitle="Upload a screenshot of the client's website" 
        accept="image/*" 
        endpoint="http://127.0.0.1:8000/api/backgrounds/upload/"
        onSuccess={handleUploadSuccess}
        onError={handleUploadError}
    />
    
    <div class="mt-6">
        <div class="flex justify-between items-center mb-2">
            <h3 class="text-lg font-medium">Available Backgrounds</h3>
            <button 
                class="text-sm text-[#6256CA] hover:text-[#4a41a0]"
                onclick={() => showBackgroundList = !showBackgroundList}
            >
                {showBackgroundList ? 'Hide' : 'Show'} ({adminStore.backgrounds.length})
            </button>
        </div>
        
        {#if adminStore.loading}
            <div class="flex justify-center py-4">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-4 border-t-[#6256CA] border-r-transparent border-b-[#00FF9C] border-l-transparent"></div>
            </div>
        {:else if showBackgroundList}
            {#if adminStore.backgrounds.length === 0}
                <p class="text-gray-500 text-center py-4">No backgrounds uploaded yet.</p>
            {:else}
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {#each adminStore.backgrounds as bg}
                        <div class="relative group">
                            <div 
                                class="border rounded-lg overflow-hidden cursor-pointer transition-all hover:shadow-md"
                                class:ring-2={bg.is_active}
                                class:ring-[#6256CA]={bg.is_active}
                                onclick={() => setActiveBackground(bg.id)}
                                onkeydown={(e) => handleKeyDown(e, bg.id)}
                                tabindex="0"
                                role="button"
                                aria-label={`Select background: ${bg.name}`}
                                aria-pressed={bg.is_active}
                            >
                                <div class="aspect-video bg-gray-100 overflow-hidden">
                                    <img 
                                        src={bg.image_url} 
                                        alt={bg.name} 
                                        class="w-full h-full object-cover"
                                    />
                                </div>
                                <div class="p-2">
                                    <p class="text-sm truncate">{bg.name}</p>
                                    {#if bg.is_active}
                                        <span class="text-xs text-[#00FF9C]">Active</span>
                                    {/if}
                                </div>
                            </div>
                            
                            <!-- Delete button -->
                            <button 
                                class="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                onclick={(e) => {
                                    e.stopPropagation();
                                    confirmDelete(bg.id);
                                }}
                                aria-label={`Delete background: ${bg.name}`}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        {/if}
    </div>
</div>