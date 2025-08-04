import React, { useRef, useState } from 'react';
import { useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { toast } from 'sonner';

interface MultimodalFile {
  file: File;
  preview?: string;
  type: 'image' | 'audio' | 'document';
}

interface MultimodalUploadProps {
  onFilesUploaded: (files: MultimodalFile[]) => void;
  isUploading: boolean;
  setIsUploading: (uploading: boolean) => void;
}

export function MultimodalUpload({ onFilesUploaded, isUploading, setIsUploading }: MultimodalUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<MultimodalFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const generateUploadUrl = useMutation(api.documents.generateUploadUrl);
  const saveMultimodalFile = useMutation(api.chat.saveMultimodalFile);

  const getFileType = (file: File): 'image' | 'audio' | 'document' => {
    if (file.type.startsWith('image/')) return 'image';
    if (file.type.startsWith('audio/')) return 'audio';
    return 'document';
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const multimodalFiles: MultimodalFile[] = [];

    for (const file of Array.from(files)) {
      const fileType = getFileType(file);
      const multimodalFile: MultimodalFile = {
        file,
        type: fileType
      };

      // Generate preview for images
      if (fileType === 'image') {
        const reader = new FileReader();
        reader.onload = (e) => {
          multimodalFile.preview = e.target?.result as string;
          setSelectedFiles(prev => [...prev.filter(f => f.file.name !== file.name), multimodalFile]);
        };
        reader.readAsDataURL(file);
      }

      multimodalFiles.push(multimodalFile);
    }

    setSelectedFiles(prev => [...prev, ...multimodalFiles]);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    
    try {
      const uploadedFiles: MultimodalFile[] = [];

      for (const multimodalFile of selectedFiles) {
        // Generate upload URL
        const uploadUrl = await generateUploadUrl();
        
        // Upload file
        const result = await fetch(uploadUrl, {
          method: "POST",
          headers: { "Content-Type": multimodalFile.file.type },
          body: multimodalFile.file,
        });

        if (!result.ok) {
          throw new Error(`Upload failed for ${multimodalFile.file.name}`);
        }

        const { storageId } = await result.json();
        
        // Save multimodal file metadata
        await saveMultimodalFile({
          fileName: multimodalFile.file.name,
          fileId: storageId,
          fileType: multimodalFile.type,
          mimeType: multimodalFile.file.type,
        });

        uploadedFiles.push(multimodalFile);
      }
      
      toast.success(`Successfully uploaded ${uploadedFiles.length} file(s)`);
      onFilesUploaded(uploadedFiles);
      setSelectedFiles([]);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload files");
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (fileName: string) => {
    setSelectedFiles(prev => prev.filter(f => f.file.name !== fileName));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Multimodal Upload</h3>
      
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,audio/*,.txt,.pdf,.doc,.docx,.md"
            onChange={handleFileSelect}
            disabled={isUploading}
            className="flex-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
          />
          {selectedFiles.length > 0 && (
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} file(s)`}
            </button>
          )}
        </div>

        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Selected Files:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {selectedFiles.map((multimodalFile, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {multimodalFile.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {multimodalFile.type} • {(multimodalFile.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={() => removeFile(multimodalFile.file.name)}
                      className="text-red-600 hover:text-red-800 text-sm ml-2"
                    >
                      Remove
                    </button>
                  </div>
                  
                  {multimodalFile.type === 'image' && multimodalFile.preview && (
                    <img
                      src={multimodalFile.preview}
                      alt="Preview"
                      className="w-full h-24 object-cover rounded"
                    />
                  )}
                  
                  {multimodalFile.type === 'audio' && (
                    <div className="flex items-center justify-center h-16 bg-gray-200 rounded">
                      <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM15.657 6.343a1 1 0 011.414 0A9.972 9.972 0 0119 12a9.972 9.972 0 01-1.929 5.657 1 1 0 11-1.414-1.414A7.971 7.971 0 0017 12a7.971 7.971 0 00-1.343-4.243 1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
