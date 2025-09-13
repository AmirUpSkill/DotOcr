import { FileText } from "lucide-react";

export const OCRHeader = () => {
  return (
    <header className="bg-sidebar-bg border-b border-border-color px-6 py-4">
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <FileText className="w-6 h-6 text-orange-accent" />
          <span className="text-xl font-bold text-blue-accent">dots.ocr</span>
        </div>
        <div className="text-sm text-text-gray">
          Supports image/PDF layout analysis and structured output
        </div>
      </div>
    </header>
  );
};