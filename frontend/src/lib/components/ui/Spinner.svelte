<script lang="ts">
    // Props
    let {
        size = "md",          // sm, md, lg
        color = "primary",    // primary, secondary, white
        label = "Loading...",
        showLabel = false,
        class: className = ""
    } = $props();
    
    // Compute size classes
    const sizeClasses = {
        sm: "h-4 w-4",
        md: "h-8 w-8",
        lg: "h-12 w-12"
    };
    
    // Compute color classes
    const colorClasses = {
        primary: "text-primary",
        secondary: "text-gray-400",
        white: "text-white"
    };
</script>

<div class="flex items-center justify-center {className}">
    <svg 
        class="{sizeClasses[size]} {colorClasses[color]} animate-spin" 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
    >
        <circle 
            class="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            stroke-width="4"
        ></circle>
        <path 
            class="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
    </svg>
    
    {#if showLabel}
        <span class="ml-2 text-sm font-medium {colorClasses[color]}">
            {label}
        </span>
    {/if}
</div>