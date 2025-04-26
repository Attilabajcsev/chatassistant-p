<script lang="ts">
    // frontend/src/lib/components/ui/Card.svelte
    
    // Props
    let {
        title = "",
        footer = "",
        padding = "md",    // sm, md, lg, none
        shadow = "md",     // none, sm, md, lg
        rounded = "md",    // none, sm, md, lg
        class: className = ""
    } = $props();
    
    // Compute classes based on props
    const paddingClasses = {
        none: "",
        sm: "p-3",
        md: "p-5",
        lg: "p-8"
    };
    
    const shadowClasses = {
        none: "",
        sm: "shadow-sm",
        md: "shadow",
        lg: "shadow-lg"
    };
    
    const roundedClasses = {
        none: "",
        sm: "rounded-sm",
        md: "rounded-md",
        lg: "rounded-lg"
    };
</script>

<div class="bg-white border border-gray-200 {shadowClasses[shadow]} {roundedClasses[rounded]} {className}">
    {#if title}
        <div class="border-b border-gray-200 px-5 py-3">
            <h3 class="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
    {/if}
    
    <div class={paddingClasses[padding]}>
        <slot></slot>
    </div>
    
    {#if footer}
        <div class="border-t border-gray-200 px-5 py-3">
            {footer}
        </div>
    {/if}
</div>