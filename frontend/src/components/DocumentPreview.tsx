import { FileText } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useState, useEffect } from "react";
import { EmbedPDF } from '@simplepdf/react-embed-pdf';

interface DocumentPreviewProps {
  file: File | null;
  isLoading: boolean;
}

export const DocumentPreview = ({ file, isLoading }: DocumentPreviewProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [fileURL, setFileURL] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      setFileURL(null);
      return;
    }

    if (file.type === "application/pdf") {
      // Create blob URL for PDF viewing
      const url = URL.createObjectURL(file);
      setFileURL(url);
      setPreview(`PDF Document: ${file.name}`);
      
      // Cleanup function
      return () => {
        URL.revokeObjectURL(url);
      };
    } else if (file.type.startsWith("image/")) {
      // For images, create a data URL for preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      setFileURL(null);
    } else {
      setPreview(`File: ${file.name}`);
      setFileURL(null);
    }
  }, [file]);
  const sampleContent = `
    AMIR ABDALLAH
    
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
    • Technologies: React, Node.js, Stripe API
  `;

  if (!file) {
    return (
      <div className="flex-1 flex items-center justify-center bg-panel-bg border-r border-border-color">
        <div className="text-center">
          <FileText className="w-16 h-16 text-text-gray mx-auto mb-4" />
          <p className="text-text-gray">Upload a document to preview</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-panel-bg border-r border-border-color p-4">
      <Card className="h-full bg-card-bg border-border-color p-4 overflow-y-auto">
        <div className="mb-4">
          <h3 className="font-semibold text-foreground mb-2">Document Preview</h3>
          <div className="text-sm text-text-gray">
            {file.name} • {(file.size / 1024).toFixed(1)} KB
          </div>
        </div>
        
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-pulse text-text-gray">Loading document...</div>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none h-full">
            {file?.type === "application/pdf" && fileURL ? (
              <div className="h-full">
                <EmbedPDF
                  companyIdentifier="react-viewer"
                  mode="inline"
                  style={{ width: "100%", height: "100%", minHeight: "600px" }}
                  documentURL={fileURL}
                />
              </div>
            ) : file?.type.startsWith("image/") && preview && preview.startsWith("data:") ? (
              <div className="bg-white p-4 rounded-lg">
                <img 
                  src={preview} 
                  alt="Document preview" 
                  className="max-w-full h-auto rounded border"
                />
              </div>
            ) : (
              <div className="bg-white p-6 rounded-lg text-gray-900 font-mono text-sm leading-relaxed whitespace-pre-line">
                {file?.type === "application/pdf" 
                  ? `📄 PDF Document Preview\n\nFile: ${file.name}\nSize: ${(file.size / 1024).toFixed(1)} KB\n\nLoading PDF viewer...`
                  : sampleContent
                }
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};