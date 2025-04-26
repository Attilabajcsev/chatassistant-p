<script lang="ts">
    import type { Settings, Message } from "$lib/types";
    
    let { settings, placeholder = "Kérdezz valamit..." }: { settings: Settings, placeholder: string } = $props();
    let message = $state("");
    let loading = $state(false);
    let termsAccepted = $state(false);
    let messageAreaEl: HTMLDivElement | null = $state(null);
    let conversationID = $state(null);

    let messages: Message[] = $state([
        {
            role: "agent",
            text: settings.welcomeMessage
        }
    ]);
    
    // Auto-scroll to bottom whenever messages change
    $effect(() => {
        if (messageAreaEl && messages.length > 0) {
            scrollToBottom();
        }
    });
    
    // Function to scroll to bottom of chat
    function scrollToBottom() {
        if (messageAreaEl) {
            setTimeout(() => {
                messageAreaEl.scrollTop = messageAreaEl.scrollHeight;
            }, 10);
        }
    }
    
    async function handleSend() {
        if (!message.trim()) return;
        let newMessage = message;
        message = "";
        
        messages.push({
            role: "user",
            text: newMessage
        });
        
        // Set loading state
        loading = true;

        try {
            let response = await fetch("/chat", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    message: newMessage,
                    conversation_id: conversationID
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            let responseJSON = await response.json();
            messages.push({
                role: "agent",
                text: responseJSON.response
            });
            conversationID = responseJSON.conversation_id;

        } catch (e) {
            messages.push({
                role: "agent",
                text: "Something went wrong"
            });
        } finally {
            loading = false;
        }
    }
    
    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === "Enter" && !e.shiftKey) {
             e.preventDefault();
             handleSend();
        }
    }
</script>

{#if !termsAccepted}
    <div class="flex flex-col h-full p-6 bg-white justify-center">
        <div class="text-center max-w-md mx-auto">
            <h2 class="text-xl font-bold mb-4" style="color: var(--chat-primary, var(--color-primary));">{settings.disclaimerTitle}</h2>
            <p class="mb-4 text-left">{settings.disclaimerIntro}</p>
            <ul class="list-disc pl-5 mb-4 space-y-2 text-left">
                 {#each settings.disclaimerPoints as point}
                     {#if point} <li>{point}</li>
                    {/if}
                {/each}
            </ul>
            <div class="mt-6 flex justify-center space-x-4">
                <button
                    onclick={() => termsAccepted = true}
                    class="px-6 py-2 rounded chat-accept-button"
                    style="background-color: var(--chat-action-button, var(--color-primary)); color: var(--color-white);"
                >
                    {settings.acceptButtonText}
                </button>
            </div>
        </div>
    </div>
{:else}
    <div class="flex flex-col h-full overflow-hidden min-h-0 text-md" style="background-color: var(--bg-light); color: var(--text-dark);">
        <div bind:this={messageAreaEl} class="flex-1 overflow-y-auto min-h-0 px-4 py-6 space-y-4 message-area">
             {#each messages as msg, i (i)}
                <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
                    <div class="max-w-lg px-4 py-2 rounded-lg text-md leading-relaxed break-words chat-message" 
                         class:user-message={msg.role === 'user'}
                         class:agent-message={msg.role === 'agent'}>
                        {@html msg.text}
                    </div>
                 </div>
             {/each}
             {#if loading}
                 <div class="flex justify-start">
                    <div class="bg-neutral-200 px-4 py-2 rounded-lg animate-pulse" style="background-color: var(--bg-card);">...</div>
                 </div>
             {/if}
        </div>
        <div class="message-input-area" style="background-color: var(--bg-card); border-top: 1px solid var(--border-light);">
             <div class="flex flex-col">
                <textarea
                    bind:value={message}
                    onkeydown={handleKeyDown}
                    {placeholder}
                    rows="3"
                    class="w-full resize-none rounded-lg mb-2 p-3 border border-gray-300 focus:ring-2 focus:ring-purple-300 focus:border-purple-300"
                    style="background-color: white; color: #1f2937; min-height: 80px; outline: none;"
                    disabled={loading}
                ></textarea>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500"></span>
                    <button
                        onclick={handleSend}
                        class="px-6 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed chat-send-button"
                        style="background-color: var(--chat-action-button, var(--color-primary)); color: var(--button-text, white); transition: background-color 0.3s; cursor: pointer; border: none;"
                        disabled={loading || !message.trim()}
                    >
                        {settings.sendButtonText}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    /* Optional scrollbar styles */
    .overflow-y-auto::-webkit-scrollbar { width: 6px; }
    .overflow-y-auto::-webkit-scrollbar-track { background: transparent; }
    .overflow-y-auto::-webkit-scrollbar-thumb { background-color: var(--border-light); border-radius: 3px; }
    
    /* Responsive message area */
    .flex-1 {
        flex: 1;
        min-height: 0;
    }
    
    .message-area {
        scroll-behavior: smooth;
    }
    
    /* Message styling */
    .chat-message {
        max-width: 85%;
        word-break: break-word;
    }
    
    .user-message {
        background-color: var(--chat-primary, var(--color-primary));
        color: var(--color-white);
    }
    
    .agent-message {
        background-color: var(--bg-card);
        color: var(--text-dark);
    }
    
    /* Input area styling */
    .message-input-area {
        padding: 16px;
        max-height: 35%;
        min-height: 120px;
    }
    
    textarea {
        background-color: white !important;
        color: #1f2937 !important;
        max-height: 120px;
    }
    
    /* Media queries for smaller screens */
    @media (max-width: 768px) {
        .chat-message {
            max-width: 90%;
        }
        
        .message-input-area {
            padding: 8px;
        }
        
        textarea {
            min-height: 60px;
        }
    }
</style>