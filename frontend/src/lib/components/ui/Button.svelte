<script lang="ts">
    // frontend/src/lib/components/ui/Button.svelte
    
    // Props
    let {
        variant = "primary",   // primary, secondary, danger, outline
        size = "md",           // sm, md, lg
        fullWidth = false,
        disabled = false,
        type = "button",
        onClick = () => {},
        class: className = ""
    } = $props();
    
    // Compute classes based on variant and size
    const variantClasses = {
        primary: "bg-primary hover:bg-primary-dark text-white",
        secondary: "bg-gray-100 hover:bg-gray-200 text-gray-800",
        danger: "bg-red-600 hover:bg-red-700 text-white",
        outline: "bg-transparent border border-primary hover:bg-primary/10 text-primary"
    };

    const sizeClasses = {
        sm: "px-3 py-1.5 text-sm",
        md: "px-4 py-2",
        lg: "px-6 py-3 text-lg"
    };
    
    $effect(() => {
        // Event handling logic can go here
    });
</script>

<button
    {type}
    class="rounded-md font-medium transition-colors {variantClasses[variant]} {sizeClasses[size]} {fullWidth ? 'w-full' : ''} {className}"
    disabled={disabled}
    on:click={onClick}
>
    <slot></slot>
</button>

<style>
    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>