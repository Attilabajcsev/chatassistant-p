// frontend/src/lib/components/admin/DocumentManager.svelte
<script lang="ts">
    import DropZone from "$lib/components/ui/DropZone.svelte";
    import { adminStore } from "$lib/stores/adminStore.svelte";
    import { onMount } from "svelte";
    
    let error = $state("");
    let success = $state("");
    let isLoading = $state(false);
    let groupedDocuments = $state({});
    
    // Delete confirmation
    let showDeleteConfirm = $state(false);
    let documentToDelete = $state(null);
    
    onMount(() => {
        fetchDocuments();
    });
    
    async function fetchDocuments() {
        isLoading = true;
        error = "";
        
        try {
            console.log("🔍 Fetching documents...");
            
            // Get auth token from cookie
            const accessToken = document.cookie
                .split('; ')
                .find(row => row.startsWith('accessToken='))
                ?.split('=')[1];
                
            if (!accessToken) {
                console.error("No access token found");
                throw new Error("Authentication required");
            }
            
            // Make direct fetch request to backend
            const response = await fetch('/documents', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            
            console.log("Document fetch status:", response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Failed to fetch documents:", errorText);
                throw new Error("Server returned an error");
            }
            
            const data = await response.json();
            console.log("Document fetch response:", data);
            
            if (data && data.documents) {
                adminStore.documents = data.documents;
                groupDocuments();
            } else {
                console.warn("No documents found in response");
                adminStore.documents = [];
                groupedDocuments = {};
            }
        } catch (err) {
            console.error("Error in fetchDocuments:", err);
            error = "Failed to fetch documents. Please try again.";
            adminStore.documents = [];
            groupedDocuments = {};
        } finally {
            isLoading = false;
        }
    }
    
    function groupDocuments() {
        // Group documents by their source
        const groups = {};
        
        adminStore.documents.forEach(doc => {
            const baseName = (doc.source || "Unknown").replace(/\s*-\s*Part\s*\d+$/i, "");
            
            if (!groups[baseName]) {
                groups[baseName] = [];
            }
            
            groups[baseName].push(doc);
        });
        
        // Sort documents within each group
        Object.keys(groups).forEach(key => {
            groups[key].sort((a, b) => {
                return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
            });
        });
        
        console.log("Grouped documents:", Object.keys(groups).length, "groups");
        groupedDocuments = groups;
    }
    
    async function handleUploadSuccess(data) {
        console.log("Upload success:", data);
        success = "Document uploaded successfully!";
        error = "";
        
        // Delay fetch to ensure backend processing is complete
        setTimeout(async () => {
            await fetchDocuments();
        }, 1000);
    }
    
    function handleUploadError(err) {
        console.error("Upload error:", err);
        error = "Failed to upload document. Please try again.";
        success = "";
    }
    
    function confirmDeleteDocument(sourceKey) {
        const docsToDelete = groupedDocuments[sourceKey];
        if (docsToDelete && docsToDelete.length > 0) {
            documentToDelete = {
                id: docsToDelete[0].id,
                source: sourceKey
            };
            showDeleteConfirm = true;
        }
    }
    
    async function deleteDocument() {
        if (!documentToDelete) return;
        
        try {
            const response = await fetch(`/documents/${documentToDelete.id}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error("Failed to delete document");
            }
            
            success = `Document "${documentToDelete.source}" deleted successfully.`;
            error = "";
            await fetchDocuments();
        } catch (err) {
            console.error("Error deleting document:", err);
            error = "Failed to delete document. Please try again.";
            success = "";
        } finally {
            showDeleteConfirm = false;
            documentToDelete = null;
        }
    }
    
    function cancelDelete() {
        showDeleteConfirm = false;
        documentToDelete = null;
    }
</script>

<div class="p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-xl font-semibold mb-4">Document Manager</h2>
    
    {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
        </div>
    {/if}
    
    {#if success}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
        </div>
    {/if}
    
    <!-- Delete Confirmation Dialog -->
    {#if showDeleteConfirm}
        <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div class="bg-white p-6 rounded-lg shadow-lg max-w-md">
                <h3 class="text-lg font-semibold mb-4">Confirm Document Deletion</h3>
                <p class="mb-4">Are you sure you want to delete this document? This action cannot be undone.</p>
                
                <div class="flex justify-end space-x-4">
                    <button 
                        class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                        onclick={cancelDelete}
                    >
                        Cancel
                    </button>
                    <button 
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                        onclick={deleteDocument}
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    {/if}
    
    <DropZone 
        title="Upload Document" 
        subtitle="Drag & drop PDF or text file to update the knowledge base" 
        accept="application/pdf,.pdf,.txt,text/plain"
        endpoint="/documents/upload-pdf/"
        onSuccess={handleUploadSuccess}
        onError={handleUploadError}
    />
    
    <div class="mt-6">
        <h3 class="text-lg font-medium mb-3">Available Documents</h3>
        
        {#if isLoading}
            <div class="flex justify-center py-4">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent"></div>
            </div>
        {:else if Object.keys(groupedDocuments).length === 0}
            <p class="text-gray-500 text-center py-4">No documents uploaded yet.</p>
        {:else}
            <div class="grid grid-cols-1 gap-4">
                {#each Object.keys(groupedDocuments) as sourceKey}
                    <div class="border rounded-lg overflow-hidden">
                        <div class="flex justify-between items-center bg-gray-50 px-4 py-3 border-b">
                            <div>
                                <h4 class="font-medium">{sourceKey}</h4>
                                <p class="text-sm text-gray-500">{groupedDocuments[sourceKey].length} chunks</p>
                            </div>
                            <div class="flex gap-2">
                                <button 
                                    class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                                    onclick={() => confirmDeleteDocument(sourceKey)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                        <div>
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chunk</th>
                                        <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Added</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    {#each groupedDocuments[sourceKey] as doc}
                                        <tr>
                                            <td class="px-4 py-2 whitespace-nowrap">
                                                <div class="text-sm font-medium text-gray-900">{doc.title}</div>
                                            </td>
                                            <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(doc.created_at).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>