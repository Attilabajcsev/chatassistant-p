<script lang="ts">
    let { chatName, show = $bindable(false) }: { chatName:string, show: boolean } = $props();
</script>

<div class="relative flex items-center justify-between px-4 py-3 border-b" style="background-color: var(--bg-light); border-color: var(--border-light); border-top-left-radius: 0.75rem; border-top-right-radius: 0.75rem;">
    <div class="flex items-center">
        <div class="w-6 h-6 rounded-full mr-2" style="background-color: var(--color-primary);"></div>
        <span class="text-lg font-medium" style="color: var(--text-dark);">{chatName}</span>
    </div>
    <button
        class="p-1 transition text-neutral-500 hover:text-neutral-700"
        aria-label="close"
        onclick={() => show = false}
        style="color: var(--color-secondary);"
    >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 cursor-pointer" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
    </button>
</div>