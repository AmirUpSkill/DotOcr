import { useState } from "react";
import { OCRHeader } from "./OCRHeader";
import { Sidebar } from "./Sidebar";
import { DocumentPreview } from "./DocumentPreview";
import { OutputPanel } from "./OutputPanel";
import { apiService, type ParseResponse } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

export const OCRInterface = () => {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasOutput, setHasOutput] = useState(false);
  const [outputData, setOutputData] = useState<ParseResponse | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setHasOutput(false);
  };

  const handleParse = async (file: File, promptId: string) => {
    setIsLoading(true);
    setHasOutput(false);
    setOutputData(null);
    
    try {
      const result = await apiService.parseDocument(file, promptId);
      setOutputData(result);
      setHasOutput(true);
      
      toast({
        title: "Success!",
        description: "Document parsed successfully",
      });
    } catch (error) {
      console.error('Parse error:', error);
      toast({
        title: "Parse Error", 
        description: error instanceof Error ? error.message : "Failed to parse document",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <OCRHeader />
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          onFileSelect={handleFileSelect}
          onParse={handleParse}
          isLoading={isLoading}
        />
        
        <DocumentPreview
          file={selectedFile}
          isLoading={isLoading}
        />
        
        <OutputPanel
          hasOutput={hasOutput}
          isLoading={isLoading}
          outputData={outputData?.data || null}
          metadata={outputData?.metadata || null}
        />
      </div>
    </div>
  );
};