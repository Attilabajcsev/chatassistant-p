<script lang="ts">
    // Reusable drag & drop component that will also be used for documents later
    
    let {
        title = "Drag & Drop Files",
        subtitle = "or click to browse",
        accept = "image/*",  // Default to images, can be changed for documents
        multiple = false,
        endpoint = "",       // API endpoint to upload to
        onSuccess = (data: any) => {},
        onError = (error: any) => {}
    } = $props();
    
    let isDragging = $state(false);
    let isUploading = $state(false);
    let dropZoneRef: HTMLDivElement;
    let fileInputRef: HTMLInputElement;
    
    function handleDragEnter(e: DragEvent) {
        e.preventDefault();
        e.stopPropagation();
        isDragging = true;
    }
    
    function handleDragLeave(e: DragEvent) {
        e.preventDefault();
        e.stopPropagation();
        isDragging = false;
    }
    
    function handleDragOver(e: DragEvent) {
        e.preventDefault();
        e.stopPropagation();
        isDragging = true;
    }
    
    async function handleDrop(e: DragEvent) {
        e.preventDefault();
        e.stopPropagation();
        isDragging = false;
        
        if (!e.dataTransfer?.files.length) return;
        
        const files = e.dataTransfer.files;
        await uploadFiles(files);
    }
    
    function handleFileInputChange(e: Event) {
        const inputEl = e.target as HTMLInputElement;
        if (!inputEl.files?.length) return;
        
        uploadFiles(inputEl.files);
    }
    
    function openFileDialog() {
        fileInputRef.click();
    }
    
    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openFileDialog();
        }
    }
    
    async function uploadFiles(files: FileList) {
        if (!endpoint) {
            console.error("No upload endpoint provided");
            onError("No upload endpoint provided");
            return;
        }
        
        isUploading = true;
        
        try {
            const formData = new FormData();
            
            // We'll only handle the first file in case of multiple selections
            // unless multiple is explicitly enabled
            const file = files[0];
            
            // Determine the file type
            const isImage = file.type.startsWith('image/');
            const isPDF = file.type === 'application/pdf';
            const isText = file.type === 'text/plain';
            
            // If uploading backgrounds
            if (isImage) {
                formData.append('background_image', file);
                formData.append('name', file.name);
                formData.append('is_active', 'true');
            } 
            // If uploading PDF documents
            else if (isPDF) {
                console.log("Uploading PDF document:", file.name);
                formData.append('pdf_file', file);
                formData.append('title', file.name);
            }
            // If uploading text documents
            else if (isText) {
                console.log("Uploading text document:", file.name);
                formData.append('document', file);
                formData.append('title', file.name);
            }
            // Generic file upload
            else {
                console.log("Uploading generic file:", file.name);
                formData.append('file', file);
            }
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed with status: ${response.status}`);
            }
            
            const data = await response.json();
            onSuccess(data);
            
        } catch (error) {
            console.error("Error uploading files:", error);
            onError(error);
        } finally {
            isUploading = false;
            // Clear the file input
            fileInputRef.value = '';
        }
    }
</script>

<div 
    bind:this={dropZoneRef}
    class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
    class:border-gray-300={!isDragging}
    class:border-blue-500={isDragging}
    class:bg-gray-50={!isDragging}
    class:bg-blue-50={isDragging}
    ondragenter={handleDragEnter}
    ondragleave={handleDragLeave}
    ondragover={handleDragOver}
    ondrop={handleDrop}
    onclick={openFileDialog}
    onkeydown={handleKeyDown}
    tabindex="0"
    role="button"
    aria-label="Upload file area"
    style="min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;"
>
    <input 
        type="file" 
        bind:this={fileInputRef}
        class="hidden" 
        {accept} 
        {multiple}
        onchange={handleFileInputChange}
    />
    
    {#if isUploading}
        <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent"></div>
            <p class="mt-2">Uploading...</p>
        </div>
    {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <h3 class="text-lg font-semibold">{title}</h3>
        <p class="text-sm text-gray-500 mt-1">{subtitle}</p>
        
        {#if accept.includes('image')}
            <p class="text-xs text-gray-400 mt-2">Accepted formats: JPG, PNG, GIF, SVG</p>
        {:else if accept.includes('application/pdf')}
            <p class="text-xs text-gray-400 mt-2">Accepted format: PDF</p>
        {:else}
            <p class="text-xs text-gray-400 mt-2">Upload files here</p>
        {/if}
    {/if}
</div>