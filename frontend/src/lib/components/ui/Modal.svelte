<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    
    // Props
    let {
        isOpen = $bindable(false),
        title = "",
        size = "md",  // sm, md, lg, xl, full
        closeOnEscape = true,
        closeOnOutsideClick = true,
        onClose = () => {}
    } = $props();
    
    // State
    let modalElement: HTMLDivElement;
    
    // Size classes
    const sizeClasses = {
        sm: "max-w-md",
        md: "max-w-lg",
        lg: "max-w-2xl",
        xl: "max-w-4xl",
        full: "max-w-full mx-5"
    };
    
    // Handle escape key
    function handleKeydown(e: KeyboardEvent) {
        if (isOpen && closeOnEscape && e.key === "Escape") {
            isOpen = false;
            onClose();
        }
    }
    
    // Handle outside click
    function handleOutsideClick(e: MouseEvent) {
        if (isOpen && closeOnOutsideClick && modalElement && !modalElement.contains(e.target as Node)) {
            isOpen = false;
            onClose();
        }
    }
    
    // Add event listeners
    onMount(() => {
        document.addEventListener('keydown', handleKeydown);
        document.addEventListener('mousedown', handleOutsideClick);
        
        return () => {
            document.removeEventListener('keydown', handleKeydown);
            document.removeEventListener('mousedown', handleOutsideClick);
        };
    });
    
    // Clean up on destroy
    onDestroy(() => {
        document.removeEventListener('keydown', handleKeydown);
        document.removeEventListener('mousedown', handleOutsideClick);
    });
</script>

{#if isOpen}
    <div class="fixed inset-0 z-50 overflow-y-auto">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
        
        <!-- Modal dialog -->
        <div class="flex min-h-full items-center justify-center p-4 text-center">
            <div 
                bind:this={modalElement}
                class="w-full {sizeClasses[size]} transform overflow-hidden rounded-lg bg-white text-left align-middle shadow-xl transition-all"
            >
                {#if title}
                    <div class="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                        <h3 class="text-lg font-semibold text-gray-900">{title}</h3>
                        <button 
                            type="button"
                            class="text-gray-400 hover:text-gray-500"
                            on:click={() => {
                                isOpen = false;
                                onClose();
                            }}
                        >
                            <span class="sr-only">Close</span>
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                {/if}
                
                <div class="px-6 py-4">
                    <slot></slot>
                </div>
                
                <div class="border-t border-gray-200 px-6 py-4 flex justify-end space-x-3">
                    <slot name="footer"></slot>
                </div>
            </div>
        </div>
    </div>
{/if}