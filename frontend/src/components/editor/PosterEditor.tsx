'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Save, 
  Undo, 
  Redo, 
  Download, 
  Type, 
  Square, 
  Circle,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Trash2,
  Copy
} from 'lucide-react';

interface PosterEditorProps {
  poster: {
    id: string;
    imageUrl: string;
    prompt: string;
    metadata: unknown;
  };
  onClose: () => void;
  onSave: (editedPoster: unknown) => void;
}

interface EditorState {
  canvas: unknown | null; // fabric.Canvas - using unknown to avoid SSR issues
  history: string[];
  historyIndex: number;
  selectedObject: unknown | null; // fabric.Object - using unknown to avoid SSR issues
}

export function PosterEditor({ poster, onClose, onSave }: PosterEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [editorState, setEditorState] = useState<EditorState>({
    canvas: null,
    history: [],
    historyIndex: -1,
    selectedObject: null
  });
  
  const [textInput, setTextInput] = useState('');
  const [fontSize, setFontSize] = useState(24);
  const [fontFamily, setFontFamily] = useState('Arial');
  const [textColor, setTextColor] = useState('#000000');
  const [shapeType, setShapeType] = useState<'rect' | 'circle'>('rect');
  const [shapeColor, setShapeColor] = useState('#ff0000');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Import fabric.js only on client side
    import('fabric').then((fabricModule) => {
      const { fabric } = fabricModule;
      
      const canvas = new fabric.Canvas(canvasRef.current!, {
        width: 800,
        height: 800,
        backgroundColor: '#ffffff'
      });

      // Load the poster image
      fabric.Image.fromURL(poster.imageUrl, (img) => {
      if (img) {
        // Scale image to fit canvas
        const scale = Math.min(800 / img.width!, 800 / img.height!);
        img.scale(scale);
        img.set({
          left: (800 - img.width! * scale) / 2,
          top: (800 - img.height! * scale) / 2,
          selectable: true,
          evented: true
        });
        canvas.add(img);
        canvas.renderAll();
        saveToHistory();
      }
      setIsLoading(false);
    });

      // Event listeners
      canvas.on('selection:created', handleSelection);
      canvas.on('selection:updated', handleSelection);
      canvas.on('selection:cleared', handleSelectionCleared);
      canvas.on('object:modified', saveToHistory);

      setEditorState(prev => ({ ...prev, canvas }));

      return () => {
        canvas.dispose();
      };
    }).catch((error) => {
      console.error('Failed to load fabric.js:', error);
      setIsLoading(false);
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [poster.imageUrl]);

  const saveToHistory = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { toJSON: () => unknown };
    const state = JSON.stringify(canvas.toJSON());
    setEditorState(prev => {
      const newHistory = prev.history.slice(0, prev.historyIndex + 1);
      newHistory.push(state);
      return {
        ...prev,
        history: newHistory,
        historyIndex: newHistory.length - 1
      };
    });
  };

  const handleSelection = (e: { selected?: unknown[] }) => {
    const activeObject = e.selected?.[0] || null;
    setEditorState(prev => ({ ...prev, selectedObject: activeObject }));
  };

  const handleSelectionCleared = () => {
    setEditorState(prev => ({ ...prev, selectedObject: null }));
  };

  const addText = async () => {
    if (!editorState.canvas || !textInput.trim()) return;

    const { fabric } = await import('fabric');
    const text = new fabric.Text(textInput, {
      left: 100,
      top: 100,
      fontSize: fontSize,
      fontFamily: fontFamily,
      fill: textColor,
      selectable: true,
      evented: true
    });

    const canvas = editorState.canvas as { add: (obj: unknown) => void; setActiveObject: (obj: unknown) => void; renderAll: () => void };
    canvas.add(text);
    canvas.setActiveObject(text);
    canvas.renderAll();
    saveToHistory();
    setTextInput('');
  };

  const addShape = async () => {
    if (!editorState.canvas) return;

    const { fabric } = await import('fabric');
    let shape: unknown;
    
    if (shapeType === 'rect') {
      shape = new fabric.Rect({
        left: 100,
        top: 100,
        width: 100,
        height: 100,
        fill: shapeColor,
        selectable: true,
        evented: true
      });
    } else {
      shape = new fabric.Circle({
        left: 100,
        top: 100,
        radius: 50,
        fill: shapeColor,
        selectable: true,
        evented: true
      });
    }

    const canvas = editorState.canvas as { add: (obj: unknown) => void; setActiveObject: (obj: unknown) => void; renderAll: () => void };
    canvas.add(shape);
    canvas.setActiveObject(shape);
    canvas.renderAll();
    saveToHistory();
  };

  const deleteSelected = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const canvas = editorState.canvas as { remove: (obj: unknown) => void; renderAll: () => void };
    canvas.remove(editorState.selectedObject);
    canvas.renderAll();
    saveToHistory();
  };

  const duplicateSelected = async () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const obj = editorState.selectedObject as { clone: (callback: (cloned: unknown) => void) => void; left?: number; top?: number };
    obj.clone(async (cloned: unknown) => {
      const clonedObj = cloned as { set: (props: { left: number; top: number }) => void };
      clonedObj.set({
        left: ((obj.left as number) || 0) + 20,
        top: ((obj.top as number) || 0) + 20
      });
      const canvas = editorState.canvas as { add: (obj: unknown) => void; setActiveObject: (obj: unknown) => void; renderAll: () => void };
      canvas.add(cloned);
      canvas.setActiveObject(cloned);
      canvas.renderAll();
      saveToHistory();
    });
  };

  const rotateSelected = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const obj = editorState.selectedObject as { angle?: number; set: (prop: string, value: number) => void };
    const currentAngle = obj.angle || 0;
    obj.set('angle', currentAngle + 90);
    const canvas = editorState.canvas as { renderAll: () => void };
    canvas.renderAll();
    saveToHistory();
  };

  const bringToFront = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const canvas = editorState.canvas as { bringToFront: (obj: unknown) => void; renderAll: () => void };
    canvas.bringToFront(editorState.selectedObject);
    canvas.renderAll();
    saveToHistory();
  };

  const sendToBack = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const canvas = editorState.canvas as { sendToBack: (obj: unknown) => void; renderAll: () => void };
    canvas.sendToBack(editorState.selectedObject);
    canvas.renderAll();
    saveToHistory();
  };

  const zoomIn = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { getZoom: () => number; setZoom: (zoom: number) => void; renderAll: () => void };
    const currentZoom = canvas.getZoom();
    canvas.setZoom(Math.min(currentZoom * 1.2, 3));
    canvas.renderAll();
  };

  const zoomOut = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { getZoom: () => number; setZoom: (zoom: number) => void; renderAll: () => void };
    const currentZoom = canvas.getZoom();
    canvas.setZoom(Math.max(currentZoom / 1.2, 0.1));
    canvas.renderAll();
  };

  const resetZoom = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { setZoom: (zoom: number) => void; renderAll: () => void };
    canvas.setZoom(1);
    canvas.renderAll();
  };

  const undo = () => {
    if (editorState.historyIndex > 0 && editorState.canvas) {
      const newIndex = editorState.historyIndex - 1;
      const state = editorState.history[newIndex];
      const canvas = editorState.canvas as { loadFromJSON: (json: string, callback: () => void) => void; renderAll: () => void };
      canvas.loadFromJSON(state, () => {
        canvas.renderAll();
      });
      setEditorState(prev => ({ ...prev, historyIndex: newIndex }));
    }
  };

  const redo = () => {
    if (editorState.historyIndex < editorState.history.length - 1 && editorState.canvas) {
      const newIndex = editorState.historyIndex + 1;
      const state = editorState.history[newIndex];
      const canvas = editorState.canvas as { loadFromJSON: (json: string, callback: () => void) => void; renderAll: () => void };
      canvas.loadFromJSON(state, () => {
        canvas.renderAll();
      });
      setEditorState(prev => ({ ...prev, historyIndex: newIndex }));
    }
  };

  const exportCanvas = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { toDataURL: (options: { format: string; quality: number; multiplier: number }) => string };
    const dataURL = canvas.toDataURL({
      format: 'png',
      quality: 1,
      multiplier: 2
    });
    
    const link = document.createElement('a');
    link.download = `edited-poster-${poster.id}.png`;
    link.href = dataURL;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSave = () => {
    if (!editorState.canvas) return;
    
    const canvas = editorState.canvas as { toDataURL: (options: { format: string; quality: number; multiplier: number }) => string; toJSON: () => unknown };
    const editedData = {
      ...poster,
      editedImageUrl: canvas.toDataURL({
        format: 'png',
        quality: 1,
        multiplier: 2
      }),
      canvasData: canvas.toJSON()
    };
    
    onSave(editedData);
  };

  const fontFamilies = [
    'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana',
    'Courier New', 'Impact', 'Comic Sans MS', 'Trebuchet MS', 'Arial Black'
  ];

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-6xl h-[90vh]">
          <CardContent className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p>Loading editor...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-6xl h-[90vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle>Edit Poster</CardTitle>
          <div className="flex gap-2">
            <Button onClick={handleSave} size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button onClick={onClose} variant="outline" size="sm">
              Close
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex gap-4 overflow-hidden">
          {/* Toolbar */}
          <div className="w-64 space-y-4 overflow-y-auto">
            {/* History Controls */}
            <div className="space-y-2">
              <Label>History</Label>
              <div className="flex gap-2">
                <Button 
                  onClick={undo} 
                  disabled={editorState.historyIndex <= 0}
                  size="sm" 
                  variant="outline"
                >
                  <Undo className="h-4 w-4" />
                </Button>
                <Button 
                  onClick={redo} 
                  disabled={editorState.historyIndex >= editorState.history.length - 1}
                  size="sm" 
                  variant="outline"
                >
                  <Redo className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Zoom Controls */}
            <div className="space-y-2">
              <Label>Zoom</Label>
              <div className="flex gap-2">
                <Button onClick={zoomOut} size="sm" variant="outline">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button onClick={resetZoom} size="sm" variant="outline">
                  100%
                </Button>
                <Button onClick={zoomIn} size="sm" variant="outline">
                  <ZoomIn className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Text Tools */}
            <div className="space-y-2">
              <Label>Add Text</Label>
              <div className="space-y-2">
                <Input
                  placeholder="Enter text..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Size</Label>
                    <Input
                      type="number"
                      value={fontSize}
                      onChange={(e) => setFontSize(Number(e.target.value))}
                      className="h-8"
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Color</Label>
                    <Input
                      type="color"
                      value={textColor}
                      onChange={(e) => setTextColor(e.target.value)}
                      className="h-8"
                    />
                  </div>
                </div>
                <select
                  value={fontFamily}
                  onChange={(e) => setFontFamily(e.target.value)}
                  className="w-full p-2 border rounded text-sm"
                >
                  {fontFamilies.map(font => (
                    <option key={font} value={font}>{font}</option>
                  ))}
                </select>
                <Button onClick={addText} size="sm" className="w-full">
                  <Type className="h-4 w-4 mr-2" />
                  Add Text
                </Button>
              </div>
            </div>

            {/* Shape Tools */}
            <div className="space-y-2">
              <Label>Add Shape</Label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShapeType('rect')}
                    variant={shapeType === 'rect' ? 'default' : 'outline'}
                    size="sm"
                  >
                    <Square className="h-4 w-4" />
                  </Button>
                  <Button
                    onClick={() => setShapeType('circle')}
                    variant={shapeType === 'circle' ? 'default' : 'outline'}
                    size="sm"
                  >
                    <Circle className="h-4 w-4" />
                  </Button>
                </div>
                <div>
                  <Label className="text-xs">Color</Label>
                  <Input
                    type="color"
                    value={shapeColor}
                    onChange={(e) => setShapeColor(e.target.value)}
                    className="h-8"
                  />
                </div>
                <Button onClick={addShape} size="sm" className="w-full">
                  Add Shape
                </Button>
              </div>
            </div>

            {/* Object Controls */}
            {editorState.selectedObject && (
              <div className="space-y-2">
                <Label>Selected Object</Label>
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Button onClick={duplicateSelected} size="sm" variant="outline">
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button onClick={rotateSelected} size="sm" variant="outline">
                      <RotateCw className="h-4 w-4" />
                    </Button>
                    <Button onClick={deleteSelected} size="sm" variant="outline">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={bringToFront} size="sm" variant="outline">
                      <Layers className="h-4 w-4" />
                    </Button>
                    <Button onClick={sendToBack} size="sm" variant="outline">
                      <Layers className="h-4 w-4 rotate-180" />
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Export */}
            <div className="space-y-2">
              <Label>Export</Label>
              <Button onClick={exportCanvas} size="sm" className="w-full" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download PNG
              </Button>
            </div>
          </div>

          {/* Canvas */}
          <div className="flex-1 flex items-center justify-center bg-gray-100 rounded-lg">
            <canvas ref={canvasRef} className="border border-gray-300 rounded shadow-lg" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
