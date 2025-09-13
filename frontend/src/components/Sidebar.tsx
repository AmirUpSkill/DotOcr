import { useState, useEffect } from "react";
import { Upload, ChevronDown, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { apiService, type Prompt } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface SidebarProps {
  onFileSelect: (file: File) => void;
  onParse: (file: File, promptId: string) => void;
  isLoading: boolean;
}

export const Sidebar = ({ onFileSelect, onParse, isLoading }: SidebarProps) => {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<string>("");
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loadingPrompts, setLoadingPrompts] = useState(true);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  useEffect(() => {
    const loadPrompts = async () => {
      try {
        const fetchedPrompts = await apiService.getPrompts();
        setPrompts(fetchedPrompts);
        if (fetchedPrompts.length > 0) {
          setSelectedPrompt(fetchedPrompts[0].id);
        }
      } catch (error) {
        console.error('Failed to load prompts:', error);
        toast({
          title: "Error",
          description: "Failed to load prompts. Please try again.",
          variant: "destructive",
        });
      } finally {
        setLoadingPrompts(false);
      }
    };

    loadPrompts();
  }, [toast]);

  const handleExampleSelect = () => {
    // Mock example file
    const mockFile = new File(["mock content"], "Amir_Abdallah_Resume.pdf", { type: "application/pdf" });
    setSelectedFile(mockFile);
    onFileSelect(mockFile);
  };

  const formatFileSize = (bytes: number) => {
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const getSelectedPromptDescription = () => {
    const prompt = prompts.find(p => p.id === selectedPrompt);
    return prompt ? prompt.description : "Select a prompt to see its description.";
  };

  const handleParseClick = () => {
    if (selectedFile && selectedPrompt) {
      onParse(selectedFile, selectedPrompt);
    }
  };

  return (
    <div className="w-80 bg-sidebar-bg border-r border-border-color p-4 space-y-4 h-full overflow-y-auto">
      <Card className="p-4 bg-card-bg border-border-color">
        <h3 className="font-semibold text-foreground mb-3">Upload & Select</h3>
        
        <div className="space-y-3">
          <div>
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="flex items-center justify-center w-full h-24 border-2 border-dashed border-border-color rounded-lg hover:border-orange-accent transition-colors bg-hover-bg">
                <div className="text-center">
                  <Upload className="w-6 h-6 text-text-gray mx-auto mb-1" />
                  <span className="text-sm text-text-gray">Click to upload</span>
                </div>
              </div>
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>

          {selectedFile && (
            <div className="flex items-center justify-between p-2 bg-hover-bg rounded border border-border-color">
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground truncate">
                  {selectedFile.name}
                </div>
                <div className="text-xs text-text-gray">
                  {formatFileSize(selectedFile.size)}
                </div>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-text-gray hover:text-error ml-2"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="text-center">
            <span className="text-xs text-text-gray">or</span>
          </div>

          <Button
            variant="outline"
            onClick={handleExampleSelect}
            className="w-full bg-hover-bg border-border-color text-foreground hover:bg-light-gray"
          >
            Select an Example
          </Button>
        </div>
      </Card>

      <Card className="p-4 bg-card-bg border-border-color">
        <h3 className="font-semibold text-foreground mb-3">Prompt & Actions</h3>
        
        <div className="space-y-3">
          <div>
            <label className="text-sm text-text-gray mb-2 block">Select Prompt</label>
            <Select value={selectedPrompt} onValueChange={setSelectedPrompt} disabled={loadingPrompts}>
              <SelectTrigger className="bg-hover-bg border-border-color text-foreground">
                <SelectValue placeholder={loadingPrompts ? "Loading prompts..." : "Select a prompt"} />
              </SelectTrigger>
              <SelectContent className="bg-panel-bg border-border-color">
                {prompts.map((prompt) => (
                  <SelectItem key={prompt.id} value={prompt.id}>
                    {prompt.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm text-text-gray mb-2 block">Current Prompt Content</label>
            <div className="p-3 bg-hover-bg rounded border border-border-color text-xs text-light-text leading-relaxed">
              {getSelectedPromptDescription()}
            </div>
          </div>

          <Button
            onClick={handleParseClick}
            disabled={!selectedFile || !selectedPrompt || isLoading || loadingPrompts}
            className="w-full bg-orange-accent hover:bg-orange-accent/90 text-deep-black font-semibold py-2 rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            {isLoading ? "Parsing..." : "Parse"}
          </Button>
        </div>
      </Card>
    </div>
  );
};