<script lang="ts">
    import { adminStore } from "$lib/stores/adminStore.svelte"
    
    // Default values for resetting prompt
    const DEFAULT_ASSISTANT_ROLE = 
    `You are a helpful AI assistant integrated into a website. Your purpose is to provide information about the website content and answer visitor questions in a helpful manner.`;

    const DEFAULT_RESPONSE_GUIDELINES = 
    `- Provide concise and accurate answers based on the given context
    - Be friendly and professional in your tone
    - Use bullet points for lists
    - If you don't know the answer based on the provided context, admit it clearly
    - Format your responses for easy readability`;

    const DEFAULT_RESTRICTIONS = 
    `- Only answer based on the context provided or general knowledge directly related to the website's topic
    - Do not make up information or provide details not supported by the context
    - Do not provide personal opinions
    - Do not provide information on illegal activities
    - Refuse to engage with harmful, inappropriate, or offensive requests`;
    
    let successMessage = $state('');
    let errorMessage = $state('');
    let isLoading = $state(false);
    let activeTab = $state('role');
        
    async function savePrompt() {
        if (!adminStore.prompt.name?.trim()) {
            errorMessage = "Prompt name is required";
            return;
        }
        
        if (!adminStore.prompt.assistant_role?.trim()) {
            errorMessage = "Assistant role description is required";
            activeTab = 'role';
            return;
        }
        
        try {
            isLoading = true;
            
            // Simple POST to update the prompt
            const response = await fetch("/prompts", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    name: adminStore.prompt.name.trim(),
                    assistant_role: adminStore.prompt.assistant_role,
                    website_context: adminStore.prompt.website_context || '',
                    knowledge_context: adminStore.prompt.knowledge_context || '',
                    response_guidelines: adminStore.prompt.response_guidelines,
                    restrictions: adminStore.prompt.restrictions || ''
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseJSON = await response.json();
            if (responseJSON.status === 'success') {
                successMessage = "Prompt saved successfully!";
                errorMessage = '';
            } else {
                throw new Error(responseJSON.message || "Failed to save prompt");
            }
        } catch (err) {
            console.error("Error saving prompt:", err);
            errorMessage = "Failed to save prompt. Please try again.";
            successMessage = '';
        } finally {
            isLoading = false;
        }
    }
    
    function resetToDefaults() {
        if (confirm("Are you sure you want to reset to default values? This will discard all your changes.")) {
            adminStore.prompt = {
                ...adminStore.prompt,
                assistant_role: DEFAULT_ASSISTANT_ROLE,
                website_context: '',
                knowledge_context: '',
                response_guidelines: DEFAULT_RESPONSE_GUIDELINES,
                restrictions: DEFAULT_RESTRICTIONS
            };
            successMessage = "Reset to default values.";
            errorMessage = '';
        }
    }
    
</script>


<div class="p-6 bg-white rounded-lg shadow-md max-h-[calc(100vh-10rem)] overflow-y-auto">
    <h2 class="text-xl font-semibold mb-4">AI Assistant Prompt</h2>
    <p class="mb-6 text-gray-600">Configure how the AI assistant understands and responds to user queries.</p>
    
    {#if successMessage}
        <div class="alert alert-success mb-4" role="alert">{successMessage}</div>
    {/if}
    
    {#if errorMessage}
        <div class="alert alert-error mb-4" role="alert">{errorMessage}</div>
    {/if}
    
    {#if isLoading}
        <div class="flex justify-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent"></div>
        </div>
    {:else}
        <div class="mb-4">
            <label for="promptName" class="form-label">Assistant Name:</label>
            <input 
                type="text" 
                id="promptName" 
                class="form-control" 
                bind:value={adminStore.prompt.name}
                placeholder="E.g., Website Assistant, Customer Support AI, etc."
                style="background-color: white; color: #1f2937;"
            />
        </div>
        
        <!-- Tabbed navigation for different prompt sections -->
        <div class="mb-4 border-b">
            <div class="flex space-x-1">
                <button 
                    class="py-2 px-4 text-sm font-medium" 
                    class:text-blue-600={activeTab === 'role'} 
                    class:border-blue-600={activeTab === 'role'}
                    class:border-b-2={activeTab === 'role'}
                    onclick={() => activeTab = 'role'}
                >
                    Assistant Role
                </button>
                <button 
                    class="py-2 px-4 text-sm font-medium" 
                    class:text-blue-600={activeTab === 'website'} 
                    class:border-blue-600={activeTab === 'website'}
                    class:border-b-2={activeTab === 'website'}
                    onclick={() => activeTab = 'website'}
                >
                    Website Info
                </button>
                <button 
                    class="py-2 px-4 text-sm font-medium" 
                    class:text-blue-600={activeTab === 'knowledge'} 
                    class:border-blue-600={activeTab === 'knowledge'}
                    class:border-b-2={activeTab === 'knowledge'}
                    onclick={() => activeTab = 'knowledge'}
                >
                    Knowledge Base
                </button>
                <button 
                    class="py-2 px-4 text-sm font-medium" 
                    class:text-blue-600={activeTab === 'guidelines'} 
                    class:border-blue-600={activeTab === 'guidelines'}
                    class:border-b-2={activeTab === 'guidelines'}
                    onclick={() => activeTab = 'guidelines'}
                >
                    Guidelines
                </button>
                <button 
                    class="py-2 px-4 text-sm font-medium" 
                    class:text-blue-600={activeTab === 'restrictions'} 
                    class:border-blue-600={activeTab === 'restrictions'}
                    class:border-b-2={activeTab === 'restrictions'}
                    onclick={() => activeTab = 'restrictions'}
                >
                    Restrictions
                </button>
            </div>
        </div>
        
        <!-- Tab content -->
        {#if activeTab === 'role'}
            <div class="mb-4">
                <label for="assistant_role" class="form-label">Assistant Role & Purpose:</label>
                <textarea 
                    id="assistant_role" 
                    class="form-control font-mono text-sm"
                    rows="8"
                    bind:value={adminStore.prompt.assistant_role}
                    placeholder="Define who the assistant is and its general purpose..."
                    style="background-color: white; color: #1f2937;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Define the assistant's identity, tone and primary purpose.
                </p>
            </div>
        {:else if activeTab === 'website'}
            <div class="mb-4">
                <label for="website_context" class="form-label">Website/Company Context:</label>
                <textarea 
                    id="website_context" 
                    class="form-control font-mono text-sm"
                    rows="8"
                    bind:value={adminStore.prompt.website_context}
                    placeholder="Add general information about the website, company or service..."
                    style="background-color: white; color: #1f2937;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Include information about the organization, product or service the AI represents.
                </p>
            </div>
        {:else if activeTab === 'knowledge'}
            <div class="mb-4">
                <label for="knowledge_context" class="form-label">Fixed Knowledge Context:</label>
                <textarea 
                    id="knowledge_context" 
                    class="form-control font-mono text-sm"
                    rows="8" 
                    bind:value={adminStore.prompt.knowledge_context}
                    placeholder="Enter specific facts, terminology, or concepts the assistant should know..."
                    style="background-color: white; color: #1f2937;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    This is information that will always be available to the AI, regardless of the RAG context.
                </p>
            </div>
        {:else if activeTab === 'guidelines'}
            <div class="mb-4">
                <label for="response_guidelines" class="form-label">Response Guidelines:</label>
                <textarea 
                    id="response_guidelines" 
                    class="form-control font-mono text-sm"
                    rows="8"
                    bind:value={adminStore.prompt.response_guidelines}
                    placeholder="Define guidelines for how the assistant should format responses..."
                    style="background-color: white; color: #1f2937;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Specify tone, structure, length, and formatting preferences for responses.
                </p>
            </div>
        {:else if activeTab === 'restrictions'}
            <div class="mb-4">
                <label for="restrictions" class="form-label">Limitations & Restrictions:</label>
                <textarea 
                    id="restrictions" 
                    class="form-control font-mono text-sm"
                    rows="8"
                    bind:value={adminStore.prompt.restrictions}
                    placeholder="Define constraints or limitations on what the assistant should or shouldn't do..."
                    style="background-color: white; color: #1f2937;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Specify what topics to avoid, what the assistant should never do, etc.
                </p>
            </div>
        {/if}
        
        <div class="flex justify-end space-x-3 mt-6">
            <button 
                class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                onclick={resetToDefaults}
            >
                Reset to Defaults
            </button>
            <button 
                class="btn btn-primary"
                onclick={savePrompt}
                style="background-color: #6256CA; color: white;"
            >
                Save Prompt
            </button>
        </div>
    {/if}
</div>

<style>
    /* Override input styling */
    :global(.form-control) {
        background-color: white !important;
        color: #1f2937 !important;
    }
    
    /* Make sure buttons have correct styling */
    .btn-primary {
        background-color: #6256CA !important;
        color: white !important;
    }
    
    /* Alert styles */
    .alert { padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-width: 1px; }
    .alert-success { background-color: #d1fae5; border-color: #34d399; color: #047857; }
    .alert-error { background-color: #fee2e2; border-color: #f87171; color: #b91c1c; }
</style>