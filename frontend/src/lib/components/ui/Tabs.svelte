<script lang="ts">
    // Tab item interface
    interface TabItem {
        id: string;
        label: string;
        disabled?: boolean;
    }
    
    // Props
    let {
        tabs = [] as TabItem[],
        activeTab = $bindable(''),
        variant = "underline",  // underline, pills, bordered
        class: className = ""
    } = $props();
    
    // Set initial active tab if not provided
    $effect(() => {
        if (!activeTab && tabs.length > 0) {
            activeTab = tabs[0].id;
        }
    });
    
    // Handle tab click
    function handleTabClick(tabId: string) {
        activeTab = tabId;
    }
    
    // Compute tab style classes based on variant
    const getTabClasses = (tab: TabItem, isActive: boolean) => {
        const baseClasses = "px-4 py-2 text-sm font-medium transition-colors";
        const disabledClasses = tab.disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer";
        
        if (variant === "underline") {
            return `${baseClasses} ${disabledClasses} border-b-2 ${
                isActive 
                    ? "border-primary text-primary" 
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
            }`;
        } else if (variant === "pills") {
            return `${baseClasses} ${disabledClasses} rounded-md ${
                isActive 
                    ? "bg-primary text-white" 
                    : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            }`;
        } else if (variant === "bordered") {
            return `${baseClasses} ${disabledClasses} ${
                isActive 
                    ? "border-t border-l border-r rounded-t-md -mb-px bg-white text-primary" 
                    : "text-gray-500 hover:text-gray-700"
            }`;
        }
        
        return baseClasses;
    };
    
    // Compute tab list classes
    const getTabListClasses = () => {
        if (variant === "underline") {
            return "flex space-x-2 border-b border-gray-200";
        } else if (variant === "pills") {
            return "flex space-x-2";
        } else if (variant === "bordered") {
            return "flex space-x-2 border-b border-gray-200";
        }
        
        return "flex space-x-2";
    };
</script>

<div class={className}>
    <div class={getTabListClasses()}>
        {#each tabs as tab}
            <button 
                class={getTabClasses(tab, activeTab === tab.id)}
                disabled={tab.disabled}
                on:click={() => !tab.disabled && handleTabClick(tab.id)}
            >
                {tab.label}
            </button>
        {/each}
    </div>
    <div class="py-4">
        <slot></slot>
    </div>
</div>