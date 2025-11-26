'use client';

import React, { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Save, 
  Undo, 
  Redo, 
  Download, 
  Type, 
  Square, 
  Circle, 
  Image as ImageIcon,
  Palette,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Trash2,
  Copy,
  Move
} from 'lucide-react';

interface PosterEditorProps {
  poster: {
    id: string;
    imageUrl: string;
    prompt: string;
    metadata: any;
  };
  onClose: () => void;
  onSave: (editedPoster: any) => void;
}

interface EditorState {
  canvas: fabric.Canvas | null;
  history: string[];
  historyIndex: number;
  selectedObject: fabric.Object | null;
}

export default function PosterEditorInternal({ poster, onClose, onSave }: PosterEditorProps) {
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

    const canvas = new fabric.Canvas(canvasRef.current, {
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
  }, [poster.imageUrl]);

  const saveToHistory = () => {
    if (!editorState.canvas) return;
    
    const state = JSON.stringify(editorState.canvas.toJSON());
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

  const handleSelection = (e: fabric.IEvent) => {
    const activeObject = e.selected?.[0] || null;
    setEditorState(prev => ({ ...prev, selectedObject: activeObject }));
  };

  const handleSelectionCleared = () => {
    setEditorState(prev => ({ ...prev, selectedObject: null }));
  };

  const addText = () => {
    if (!editorState.canvas || !textInput.trim()) return;

    const text = new fabric.Text(textInput, {
      left: 100,
      top: 100,
      fontSize: fontSize,
      fontFamily: fontFamily,
      fill: textColor,
      selectable: true,
      evented: true
    });

    editorState.canvas.add(text);
    editorState.canvas.setActiveObject(text);
    editorState.canvas.renderAll();
    saveToHistory();
    setTextInput('');
  };

  const addShape = () => {
    if (!editorState.canvas) return;

    let shape: fabric.Object;
    
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

    editorState.canvas.add(shape);
    editorState.canvas.setActiveObject(shape);
    editorState.canvas.renderAll();
    saveToHistory();
  };

  const deleteSelected = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    editorState.canvas.remove(editorState.selectedObject);
    editorState.canvas.renderAll();
    saveToHistory();
  };

  const duplicateSelected = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    editorState.selectedObject.clone((cloned: fabric.Object) => {
      cloned.set({
        left: (editorState.selectedObject?.left || 0) + 20,
        top: (editorState.selectedObject?.top || 0) + 20
      });
      editorState.canvas!.add(cloned);
      editorState.canvas!.setActiveObject(cloned);
      editorState.canvas!.renderAll();
      saveToHistory();
    });
  };

  const rotateSelected = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    const currentAngle = editorState.selectedObject.angle || 0;
    editorState.selectedObject.set('angle', currentAngle + 90);
    editorState.canvas.renderAll();
    saveToHistory();
  };

  const bringToFront = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    editorState.canvas.bringToFront(editorState.selectedObject);
    editorState.canvas.renderAll();
    saveToHistory();
  };

  const sendToBack = () => {
    if (!editorState.canvas || !editorState.selectedObject) return;
    
    editorState.canvas.sendToBack(editorState.selectedObject);
    editorState.canvas.renderAll();
    saveToHistory();
  };

  const zoomIn = () => {
    if (!editorState.canvas) return;
    
    const currentZoom = editorState.canvas.getZoom();
    editorState.canvas.setZoom(Math.min(currentZoom * 1.2, 3));
    editorState.canvas.renderAll();
  };

  const zoomOut = () => {
    if (!editorState.canvas) return;
    
    const currentZoom = editorState.canvas.getZoom();
    editorState.canvas.setZoom(Math.max(currentZoom / 1.2, 0.1));
    editorState.canvas.renderAll();
  };

  const resetZoom = () => {
    if (!editorState.canvas) return;
    
    editorState.canvas.setZoom(1);
    editorState.canvas.renderAll();
  };

  const undo = () => {
    if (editorState.historyIndex > 0) {
      const newIndex = editorState.historyIndex - 1;
      const state = editorState.history[newIndex];
      editorState.canvas?.loadFromJSON(state, () => {
        editorState.canvas?.renderAll();
      });
      setEditorState(prev => ({ ...prev, historyIndex: newIndex }));
    }
  };

  const redo = () => {
    if (editorState.historyIndex < editorState.history.length - 1) {
      const newIndex = editorState.historyIndex + 1;
      const state = editorState.history[newIndex];
      editorState.canvas?.loadFromJSON(state, () => {
        editorState.canvas?.renderAll();
      });
      setEditorState(prev => ({ ...prev, historyIndex: newIndex }));
    }
  };

  const exportCanvas = () => {
    if (!editorState.canvas) return;
    
    const dataURL = editorState.canvas.toDataURL({
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
    
    const editedData = {
      ...poster,
      editedImageUrl: editorState.canvas.toDataURL({
        format: 'png',
        quality: 1,
        multiplier: 2
      }),
      canvasData: editorState.canvas.toJSON()
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

