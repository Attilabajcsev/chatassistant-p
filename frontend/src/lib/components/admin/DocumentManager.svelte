<script lang="ts">
    import DropZone from "$lib/components/ui/DropZone.svelte";
    import { adminStore } from "$lib/stores/adminStore.svelte";
    import { onMount } from "svelte";
    
    let error = $state("");
    let success = $state("");
    let isLoading = $state(false);
    let isSaving = $state(false);
    let groupedDocuments = $state({});
    
    // Track which documents are selected for activation
    let selectedDocumentIds = $state([]);
    
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
            
            // Make API request
            const response = await fetch('/documents', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            
            console.log("Document fetch response status:", response.status);
            
            if (!response.ok) {
                throw new Error(`Server returned an error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Document fetch response:", data);
            
            if (data && data.documents) {
                adminStore.documents = data.documents;
                
                // Initialize selected documents based on active status
                selectedDocumentIds = data.documents
                    .filter(doc => doc.is_active)
                    .map(doc => doc.id);
                    
                console.log("Selected document IDs:", selectedDocumentIds);
                
                groupDocuments();
            } else {
                console.warn("No documents found in response");
                adminStore.documents = [];
                selectedDocumentIds = [];
                groupedDocuments = {};
            }
        } catch (err) {
            console.error("Error in fetchDocuments:", err);
            error = "Failed to fetch documents. Please try again.";
            adminStore.documents = [];
            selectedDocumentIds = [];
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
    
    // Toggle selection of a document group
    function toggleDocumentGroup(sourceKey) {
        const docsInGroup = groupedDocuments[sourceKey] || [];
        const docIds = docsInGroup.map(doc => doc.id);
        
        // Check if all documents in this group are already selected
        const allSelected = docIds.every(id => selectedDocumentIds.includes(id));
        
        if (allSelected) {
            // If all are selected, deselect them
            selectedDocumentIds = selectedDocumentIds.filter(id => !docIds.includes(id));
        } else {
            // Otherwise, select all in this group
            // First remove any that might be selected
            const remaining = selectedDocumentIds.filter(id => !docIds.includes(id));
            selectedDocumentIds = [...remaining, ...docIds];
        }
        
        console.log("Updated selected document IDs:", selectedDocumentIds);
    }
    
    // Check if a document group is active
    function isDocumentGroupActive(sourceKey) {
        const docsInGroup = groupedDocuments[sourceKey] || [];
        // Group is active if any doc in the group is active
        return docsInGroup.some(doc => doc.is_active);
    }
    
    // Check if a document group is selected
    function isDocumentGroupSelected(sourceKey) {
        const docsInGroup = groupedDocuments[sourceKey] || [];
        const docIds = docsInGroup.map(doc => doc.id);
        // Group is selected if all docs in the group are selected
        return docIds.length > 0 && docIds.every(id => selectedDocumentIds.includes(id));
    }
    
    // Save active documents
    async function saveActiveDocuments() {
        isSaving = true;
        error = "";
        
        try {
            console.log("Saving active documents:", selectedDocumentIds);
            
            const response = await fetch('/documents/set-active', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ document_ids: selectedDocumentIds })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to set active documents: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Set active response:", data);
            
            if (data.status === 'success') {
                success = "Active documents updated successfully!";
                await fetchDocuments(); // Refresh to get updated active status
            } else {
                throw new Error(data.message || "Failed to update active documents");
            }
        } catch (err) {
            console.error("Error setting active documents:", err);
            error = typeof err === 'object' ? err.message : String(err);
            success = "";
        } finally {
            isSaving = false;
        }
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
            
            const data = await response.json();
            
            if (data.status === 'success') {
                success = `Document "${documentToDelete.source}" deleted successfully.`;
                error = "";
                await fetchDocuments();
            } else {
                throw new Error(data.message || "Failed to delete document");
            }
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
        <div class="flex justify-between items-center mb-3">
            <h3 class="text-lg font-medium">Available Documents</h3>
            <button 
                onclick={saveActiveDocuments}
                disabled={isSaving}
                class="px-4 py-2 text-white text-sm rounded flex items-center"
                style="background-color: #6256CA;"
            >
                {#if isSaving}
                    <div class="mr-2 inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-r-transparent"></div>
                {/if}
                Save Active Documents
            </button>
        </div>
        
        <p class="text-sm text-gray-500 mb-4">
            Select documents to make them available for the AI assistant to use when answering questions.
        </p>
        
        {#if isLoading}
            <div class="flex justify-center py-4">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-4" 
                     style="border-top-color: #6256CA; border-right-color: transparent; border-bottom-color: #00FF9C; border-left-color: transparent;"></div>
            </div>
        {:else if Object.keys(groupedDocuments).length === 0}
            <p class="text-gray-500 text-center py-4">No documents uploaded yet.</p>
        {:else}
            <div class="grid grid-cols-1 gap-4">
                {#each Object.keys(groupedDocuments) as sourceKey}
                    <div class="border rounded-lg overflow-hidden" 
                         style={isDocumentGroupActive(sourceKey) ? "border-color: #6256CA;" : ""}>
                        <div class="flex justify-between items-center px-4 py-3 border-b" 
                             style={isDocumentGroupActive(sourceKey) ? "background-color: rgba(98, 86, 202, 0.1);" : "background-color: #f9fafb;"}>
                            <div class="flex items-center">
                                <input 
                                    type="checkbox" 
                                    id={`group-${sourceKey}`}
                                    checked={isDocumentGroupSelected(sourceKey)}
                                    onclick={() => toggleDocumentGroup(sourceKey)}
                                    class="mr-3 h-4 w-4 rounded focus:ring-purple-500 text-purple-600"
                                />
                                <div>
                                    <h4 class="font-medium">{sourceKey}</h4>
                                    <p class="text-sm text-gray-500">{groupedDocuments[sourceKey].length} chunks</p>
                                </div>
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
                                        <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
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
                                            <td class="px-4 py-2 whitespace-nowrap text-sm">
                                                {#if doc.is_active}
                                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                                                          style="background-color: rgba(0, 255, 156, 0.2); color: #00994C;">
                                                        Active
                                                    </span>
                                                {:else}
                                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                                                        Inactive
                                                    </span>
                                                {/if}
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

<style lang="css">
    /* Style for checkboxes */
    input[type="checkbox"]:checked {
        background-color: #6256CA;
        border-color: #6256CA;
    }
    
    input[type="checkbox"]:focus {
        --tw-ring-color: rgba(98, 86, 202, 0.5);
    }
    
    /* Hover effect for save button */
    button[style*="background-color: #6256CA"]:hover {
        background-color: #4a41a0 !important;
    }
</style>