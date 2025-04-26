<script lang="ts">
    // frontend/src/lib/components/ui/Input.svelte
    
    // Props
    let {
        id = "",
        label = "",
        type = "text",
        placeholder = "",
        value = "",
        disabled = false,
        error = "",
        helper = "",
        required = false,
        class: className = ""
    } = $props();
</script>

<div class="mb-4 {className}">
    {#if label}
        <label for={id} class="block mb-2 text-sm font-medium text-gray-900">
            {label}
            {#if required}
                <span class="text-red-600">*</span>
            {/if}
        </label>
    {/if}
    
    <input
        {id}
        {type}
        {placeholder}
        {disabled}
        {required}
        class="bg-gray-50 border {error ? 'border-red-500' : 'border-gray-300'} text-gray-900 text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
        class:bg-gray-100={disabled}
        class:cursor-not-allowed={disabled}
        bind:value
    />
    
    {#if error}
        <p class="mt-2 text-sm text-red-600">
            {error}
        </p>
    {:else if helper}
        <p class="mt-2 text-sm text-gray-500">
            {helper}
        </p>
    {/if}
</div>