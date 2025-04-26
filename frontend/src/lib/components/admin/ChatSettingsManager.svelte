<script lang="ts">
    import { adminStore } from '$lib/stores/adminStore.svelte'

    let successMessage = $state('');
    let errorMessage = $state('');
    let activeSection = $state('general');

    async function handleSaveLogic() {
        errorMessage = '';
        successMessage = '';
        try {
            if (!adminStore.settings.chatName.trim()) { throw new Error('Chat Name cannot be empty.'); }
            if (!adminStore.settings.disclaimerTitle.trim()) { throw new Error('Disclaimer Title cannot be empty.'); }
            if (!adminStore.settings.welcomeMessage.trim()) { throw new Error('Welcome Message cannot be empty.'); }
            if (!adminStore.settings.acceptButtonText.trim()) { throw new Error('Accept Button Text cannot be empty.'); }
            if (!adminStore.settings.sendButtonText.trim()) { throw new Error('Send Button Text cannot be empty.'); }
            if (!adminStore.settings.footerDisclaimer.trim()) { throw new Error('Footer Disclaimer cannot be empty.'); }
            
            // Save settings using direct fetch
            const response = await fetch("/settings", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(adminStore.settings),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseJSON = await response.json();
            if (responseJSON.status === 'success') {
                successMessage = 'Settings saved successfully!';
                errorMessage = '';
            } else {
                throw new Error(responseJSON.message || "Failed to save settings");
            }
        } catch (err: any) {
            console.error("Error saving settings:", err);
            errorMessage = err.message || 'Failed to save settings.';
        }
    }

    // Function to change the active section
    function setActiveSection(section: string) {
        activeSection = section;
    }

    // Function to update disclaimer points from textarea
    function updateDisclaimerPointsFromTextarea(event: Event) {
        const textarea = event.target as HTMLTextAreaElement;
        const points = textarea.value
            .split('\n')
            .map(point => point.trim())
            .filter(point => point !== '');
        adminStore.settings.disclaimerPoints = points;
    }

</script>


<div class="p-6 bg-white rounded-lg shadow-md max-h-[calc(100vh-10rem)] overflow-y-auto">
     <h2 class="text-xl font-semibold mb-6">Chat Appearance & Text</h2>
     {#if successMessage} <div class="alert alert-success" role="alert">{successMessage}</div> {/if}
     {#if errorMessage} <div class="alert alert-error" role="alert">{errorMessage}</div> {/if}

     <!-- Section navigation tabs -->
     <div class="mb-6 border-b">
        <div class="flex space-x-2">
            <button 
                class="py-2 px-4 text-sm font-medium transition-colors"
                class:text-blue-600={activeSection === "general"} 
                class:border-blue-600={activeSection === "general"}
                class:border-b-2={activeSection === "general"}
                onclick={() => setActiveSection("general")}
            >
                General
            </button>
            <button 
                class="py-2 px-4 text-sm font-medium transition-colors"
                class:text-blue-600={activeSection === "disclaimer"} 
                class:border-blue-600={activeSection === "disclaimer"}
                class:border-b-2={activeSection === "disclaimer"}
                onclick={() => setActiveSection("disclaimer")}
            >
                Disclaimer
            </button>
            <button 
                class="py-2 px-4 text-sm font-medium transition-colors"
                class:text-blue-600={activeSection === "buttons"} 
                class:border-blue-600={activeSection === "buttons"}
                class:border-b-2={activeSection === "buttons"}
                onclick={() => setActiveSection("buttons")}
            >
                Buttons & Footer
            </button>
            <button 
                class="py-2 px-4 text-sm font-medium transition-colors"
                class:text-blue-600={activeSection === "colors"} 
                class:border-blue-600={activeSection === "colors"}
                class:border-b-2={activeSection === "colors"}
                onclick={() => setActiveSection("colors")}
            >
                Colors
            </button>
        </div>
     </div>

     <form onsubmit={handleSaveLogic}>
         <!-- General Settings Section -->
         {#if activeSection === "general"}
             <div class="mb-4">
                <label for="chatName" class="form-label">Chat Window Title & Button Name:</label>
                <input type="text" id="chatName" class="form-control" bind:value={adminStore.settings.chatName} required/>
            </div>
            
            <div class="mb-4">
                <label for="welcomeMessage" class="form-label">Initial Bot Message:</label>
                <textarea id="welcomeMessage" class="form-control" rows="4" bind:value={adminStore.settings.welcomeMessage} required></textarea>
                <p class="text-xs text-gray-500 mt-1">This is the first message shown from the assistant when a conversation starts.</p>
            </div>
         {/if}

         <!-- Disclaimer Section -->
         {#if activeSection === "disclaimer"}
             <div class="mb-4">
                <label for="disclaimerTitle" class="form-label">Disclaimer Title:</label>
                <input type="text" id="disclaimerTitle" class="form-control" bind:value={adminStore.settings.disclaimerTitle} required/>
            </div>
             <div class="mb-4">
                <label for="disclaimerIntro" class="form-label">Intro Paragraph:</label>
                <textarea id="disclaimerIntro" class="form-control" rows="3" bind:value={adminStore.settings.disclaimerIntro}></textarea>
            </div>
             <div class="mb-4">
                <label for="disclaimerPoints" class="form-label">Bullet Points (One per line):</label>
                <textarea id="disclaimerPoints" class="form-control" rows="5" value={adminStore.settings.disclaimerPoints.join('\n')} oninput={updateDisclaimerPointsFromTextarea}></textarea>
                <p class="text-xs text-gray-500 mt-1">Empty lines will be ignored.</p>
            </div>
         {/if}

         <!-- Buttons & Footer Section -->
         {#if activeSection === "buttons"}
             <div class="mb-4">
                <label for="acceptButtonText" class="form-label">Accept Button Text:</label>
                <input type="text" id="acceptButtonText" class="form-control" bind:value={adminStore.settings.acceptButtonText} required/>
                <p class="text-xs text-gray-500 mt-1">Text shown on the button to accept the disclaimer and start chatting.</p>
            </div>
            
             <div class="mb-4">
                <label for="sendButtonText" class="form-label">Send Button Text:</label>
                <input type="text" id="sendButtonText" class="form-control" bind:value={adminStore.settings.sendButtonText} required/>
                <p class="text-xs text-gray-500 mt-1">Text displayed on the button that sends messages.</p>
            </div>
            
             <div class="mb-4">
                <label for="footerDisclaimer" class="form-label">Footer Disclaimer Text:</label>
                <input type="text" id="footerDisclaimer" class="form-control" bind:value={adminStore.settings.footerDisclaimer} required/>
                <p class="text-xs text-gray-500 mt-1">The disclaimer text shown at the bottom of the chat window.</p>
            </div>
            
             <div class="mb-4">
                <label for="privacyPolicyText" class="form-label">Privacy Policy Link Text:</label>
                <input type="text" id="privacyPolicyText" class="form-control" bind:value={adminStore.settings.privacyPolicyText} required/>
                <p class="text-xs text-gray-500 mt-1">Text for the privacy policy link in the footer.</p>
            </div>
         {/if}

         <!-- Colors Section -->
         {#if activeSection === "colors"}
             <div class="grid grid-cols-2 gap-4 mb-4">
                 <div>
                     <label for="colorPrimary" class="form-label">Primary Color:</label>
                     <input type="color" id="colorPrimary" class="form-control h-10 p-1" bind:value={adminStore.settings.colorPrimary} />
                     <span class="text-xs ml-2">{adminStore.settings.colorPrimary}</span>
                     <p class="text-xs text-gray-500 mt-1">Controls the chat button and other interface elements</p>
                 </div>
                 <div>
                     <label for="buttonBg" class="form-label">Action Buttons Color:</label>
                     <input type="color" id="buttonBg" class="form-control h-10 p-1" bind:value={adminStore.settings.buttonBg} />
                     <span class="text-xs ml-2">{adminStore.settings.buttonBg}</span>
                     <p class="text-xs text-gray-500 mt-1">Controls the "Send" and "Accept" buttons only</p>
                 </div>
             </div>
         {/if}

         <div class="mt-6 text-right"> 
            <button type="submit" class="btn btn-primary">Save Settings</button> 
         </div>
     </form>
</div>

<style>
    /* Styles needed by this component */
    .alert { padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-width: 1px; }
    .alert-success { background-color: #d1fae5; border-color: #34d399; color: #047857; }
    .alert-error { background-color: #fee2e2; border-color: #f87171; color: #b91c1c; }
    .form-label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
    .form-control { 
        display: block; 
        width: 100%; 
        padding: 0.5rem 0.75rem; 
        background-color: white; 
        color: #1f2937;
        border-radius: 0.375rem; 
        border: 1px solid #d1d5db; 
    }
    .form-control:focus { 
        outline: none; 
        border-color: #6256CA; 
        box-shadow: 0 0 0 3px rgba(98, 86, 202, 0.2); 
    }
    input[type="color"] { 
        padding: 0.25rem; 
        background-color: white;
    }
    .btn { 
        padding: 0.5rem 1rem; 
        border-radius: 0.375rem; 
        font-weight: 500; 
        cursor: pointer; 
        transition: all 0.2s ease; 
    }
    .btn-primary { 
        background-color: #6256CA; 
        color: white; 
    }
    .btn-primary:hover { 
        background-color: #4a41a0; 
    }
</style>