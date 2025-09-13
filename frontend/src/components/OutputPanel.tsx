import { useState } from "react";
import { Copy, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

interface OutputPanelProps {
  hasOutput: boolean;
  isLoading: boolean;
  outputData?: {
    markdown: string;
    rawText: string;
  } | null;
  metadata?: {
    storage_key: string;
    model: string;
    processing_time_ms: number;
    request_id: string;
    file_size_kb: number;
  } | null;
}

export const OutputPanel = ({ hasOutput, isLoading, outputData, metadata }: OutputPanelProps) => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("markdown");

  const sampleMarkdown = `# AMIR ABDALLAH

**Contact Information**
- Email: amir.abdallah@email.com
- Phone: +216 XX XXX XXX
- Location: Sfax, Tunisia

## EDUCATION

**National School of Electronics and Telecommunications of Sfax**
*Engineering Degree in Telecommunications* | 2019 - 2022

## EXPERIENCE

### Proxym AI Software Engineering Intern
*June 2022 - August 2022*
- Developed machine learning models for document processing
- Implemented OCR solutions using Python and TensorFlow
- Collaborated with cross-functional teams on AI projects

### Junior Developer - TechCorp
*September 2022 - Present*
- Full-stack web development using React and Node.js
- Database design and optimization with PostgreSQL
- API development and integration

## SKILLS

**Programming Languages:** Python, JavaScript, TypeScript, Java
**Frameworks:** React, Node.js, Express, Django
**Databases:** PostgreSQL, MongoDB, Redis
**Tools:** Git, Docker, AWS, Jenkins

## PROJECTS

### Document Processing System
Built an OCR system for automated document analysis
*Technologies: Python, OpenCV, Tesseract*

### E-commerce Platform
Full-stack application with payment integration
*Technologies: React, Node.js, Stripe API*`;

  const sampleRawText = `AMIR ABDALLAH

Email: amir.abdallah@email.com | Phone: +216 XX XXX XXX
Location: Sfax, Tunisia

EDUCATION

National School of Electronics and Telecommunications of Sfax
Engineering Degree in Telecommunications
2019 - 2022

EXPERIENCE

Proxym AI Software Engineering Intern
June 2022 - August 2022
• Developed machine learning models for document processing
• Implemented OCR solutions using Python and TensorFlow
• Collaborated with cross-functional teams on AI projects

Junior Developer - TechCorp
September 2022 - Present
• Full-stack web development using React and Node.js
• Database design and optimization with PostgreSQL
• API development and integration

SKILLS

Programming Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Express, Django
Databases: PostgreSQL, MongoDB, Redis
Tools: Git, Docker, AWS, Jenkins

PROJECTS

Document Processing System
• Built an OCR system for automated document analysis
• Technologies: Python, OpenCV, Tesseract

E-commerce Platform
• Full-stack application with payment integration
• Technologies: React, Node.js, Stripe API`;

  // Use real data if available, otherwise fall back to sample data
  const markdownContent = outputData?.markdown || sampleMarkdown;
  const rawTextContent = outputData?.rawText || sampleRawText;

  const formatMarkdownForDisplay = (markdown: string) => {
    return markdown
      .replace(/\n/g, '<br/>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>');
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
    toast({
      title: "Copied to clipboard",
      description: "Content has been copied successfully",
    });
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!hasOutput && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-panel-bg">
        <div className="text-center">
          <div className="w-16 h-16 bg-card-bg rounded-lg flex items-center justify-center mx-auto mb-4">
            <Copy className="w-8 h-8 text-text-gray" />
          </div>
          <p className="text-text-gray">Parse a document to see output</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-panel-bg p-4">
      <Card className="h-full bg-card-bg border-border-color">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <div className="border-b border-border-color px-4 py-3">
            <div className="flex items-center justify-between">
              <TabsList className="bg-hover-bg">
                <TabsTrigger value="markdown" className="data-[state=active]:bg-orange-accent data-[state=active]:text-deep-black">
                  Markdown Preview
                </TabsTrigger>
                <TabsTrigger value="raw" className="data-[state=active]:bg-orange-accent data-[state=active]:text-deep-black">
                  Raw Text
                </TabsTrigger>
              </TabsList>
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const content = activeTab === 'markdown' ? markdownContent : rawTextContent;
                    handleCopy(content);
                  }}
                  className="bg-hover-bg border-border-color text-foreground hover:bg-light-gray"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const content = activeTab === 'markdown' ? markdownContent : rawTextContent;
                    const filename = `output.${activeTab === 'markdown' ? 'md' : 'txt'}`;
                    handleDownload(content, filename);
                  }}
                  className="bg-hover-bg border-border-color text-foreground hover:bg-light-gray"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </div>
          
          <div className="flex-1 overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-pulse text-text-gray">Processing document...</div>
              </div>
            ) : (
              <>
                <TabsContent value="markdown" className="h-full m-0">
                  <div className="h-full p-4 overflow-y-auto">
                    <div className="prose prose-sm max-w-none bg-white p-6 rounded-lg text-gray-900">
                      <div dangerouslySetInnerHTML={{ __html: formatMarkdownForDisplay(markdownContent) }} />
                    </div>
                    {metadata && (
                      <div className="mt-4 p-3 bg-hover-bg rounded border border-border-color text-xs text-light-text">
                        <div className="grid grid-cols-2 gap-2">
                          <div>Processing Time: {metadata.processing_time_ms}ms</div>
                          <div>Model: {metadata.model}</div>
                          <div>File Size: {metadata.file_size_kb} KB</div>
                          <div>Request ID: {metadata.request_id}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
                
                <TabsContent value="raw" className="h-full m-0">
                  <div className="h-full p-4 overflow-y-auto">
                    <pre className="bg-deep-black text-foreground p-4 rounded-lg text-sm font-mono leading-relaxed whitespace-pre-wrap">
                      {rawTextContent}
                    </pre>
                    {metadata && (
                      <div className="mt-4 p-3 bg-hover-bg rounded border border-border-color text-xs text-light-text">
                        <div className="grid grid-cols-2 gap-2">
                          <div>Processing Time: {metadata.processing_time_ms}ms</div>
                          <div>Model: {metadata.model}</div>
                          <div>File Size: {metadata.file_size_kb} KB</div>
                          <div>Request ID: {metadata.request_id}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </>
            )}
          </div>
        </Tabs>
      </Card>
    </div>
  );
};