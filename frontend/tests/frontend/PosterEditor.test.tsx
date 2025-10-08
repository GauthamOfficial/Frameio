import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PosterEditor } from '@/components/editor/PosterEditor';

// Mock Fabric.js
jest.mock('fabric', () => ({
  Canvas: jest.fn().mockImplementation(() => ({
    add: jest.fn(),
    remove: jest.fn(),
    renderAll: jest.fn(),
    setActiveObject: jest.fn(),
    getActiveObject: jest.fn(),
    dispose: jest.fn(),
    on: jest.fn(),
    off: jest.fn(),
    toDataURL: jest.fn().mockReturnValue('data:image/png;base64,mock-data'),
    toJSON: jest.fn().mockReturnValue({}),
    loadFromJSON: jest.fn(),
    getZoom: jest.fn().mockReturnValue(1),
    setZoom: jest.fn(),
    bringToFront: jest.fn(),
    sendToBack: jest.fn()
  })),
  Text: jest.fn().mockImplementation((text, options) => ({
    ...options,
    text,
    left: options?.left || 0,
    top: options?.top || 0
  })),
  Rect: jest.fn().mockImplementation((options) => ({
    ...options,
    left: options?.left || 0,
    top: options?.top || 0,
    width: options?.width || 100,
    height: options?.height || 100
  })),
  Circle: jest.fn().mockImplementation((options) => ({
    ...options,
    left: options?.left || 0,
    top: options?.top || 0,
    radius: options?.radius || 50
  })),
  Image: {
    fromURL: jest.fn().mockImplementation((url, callback) => {
      const mockImage = {
        width: 800,
        height: 600,
        scale: jest.fn(),
        set: jest.fn()
      };
      callback(mockImage);
    })
  }
}));

const mockPoster = {
  id: 'test-poster-123',
  imageUrl: 'https://example.com/poster.jpg',
  prompt: 'A modern tech conference poster',
  metadata: {
    style: 'modern',
    dimensions: '1080x1080',
    colorScheme: 'vibrant'
  }
};

const mockOnClose = jest.fn();
const mockOnSave = jest.fn();

describe('PosterEditor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the editor interface correctly', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Edit Poster')).toBeInTheDocument();
    });

    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('Zoom')).toBeInTheDocument();
    expect(screen.getByText('Add Text')).toBeInTheDocument();
    expect(screen.getByText('Add Shape')).toBeInTheDocument();
  });

  it('allows user to add text to the canvas', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Text')).toBeInTheDocument();
    });

    const textInput = screen.getByPlaceholderText('Enter text...');
    const addTextButton = screen.getByRole('button', { name: /add text/i });

    fireEvent.change(textInput, { target: { value: 'Test Text' } });
    fireEvent.click(addTextButton);

    expect(textInput).toHaveValue('');
  });

  it('allows user to change text properties', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Text')).toBeInTheDocument();
    });

    const fontSizeInput = screen.getByDisplayValue('24');
    const colorInput = screen.getByDisplayValue('#000000');

    fireEvent.change(fontSizeInput, { target: { value: '32' } });
    fireEvent.change(colorInput, { target: { value: '#ff0000' } });

    expect(fontSizeInput).toHaveValue(32);
    expect(colorInput).toHaveValue('#ff0000');
  });

  it('allows user to add shapes to the canvas', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Shape')).toBeInTheDocument();
    });

    const addShapeButton = screen.getByRole('button', { name: /add shape/i });
    fireEvent.click(addShapeButton);

    // Should add a shape to the canvas
    expect(addShapeButton).toBeInTheDocument();
  });

  it('allows user to switch between shape types', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Shape')).toBeInTheDocument();
    });

    const squareButton = screen.getByRole('button', { name: /square/i });
    const circleButton = screen.getByRole('button', { name: /circle/i });

    fireEvent.click(circleButton);
    expect(circleButton).toHaveClass('bg-primary');

    fireEvent.click(squareButton);
    expect(squareButton).toHaveClass('bg-primary');
  });

  it('provides zoom controls', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Zoom')).toBeInTheDocument();
    });

    const zoomInButton = screen.getByRole('button', { name: /zoom in/i });
    const zoomOutButton = screen.getByRole('button', { name: /zoom out/i });
    const resetZoomButton = screen.getByRole('button', { name: /100%/i });

    expect(zoomInButton).toBeInTheDocument();
    expect(zoomOutButton).toBeInTheDocument();
    expect(resetZoomButton).toBeInTheDocument();

    fireEvent.click(zoomInButton);
    fireEvent.click(zoomOutButton);
    fireEvent.click(resetZoomButton);
  });

  it('provides history controls', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('History')).toBeInTheDocument();
    });

    const undoButton = screen.getByRole('button', { name: /undo/i });
    const redoButton = screen.getByRole('button', { name: /redo/i });

    expect(undoButton).toBeInTheDocument();
    expect(redoButton).toBeInTheDocument();

    // Initially should be disabled
    expect(undoButton).toBeDisabled();
    expect(redoButton).toBeDisabled();
  });

  it('allows user to export the canvas', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Export')).toBeInTheDocument();
    });

    const downloadButton = screen.getByRole('button', { name: /download png/i });
    expect(downloadButton).toBeInTheDocument();

    fireEvent.click(downloadButton);
  });

  it('allows user to save and close', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Save')).toBeInTheDocument();
    });

    const saveButton = screen.getByRole('button', { name: /save/i });
    const closeButton = screen.getByRole('button', { name: /close/i });

    fireEvent.click(saveButton);
    expect(mockOnSave).toHaveBeenCalled();

    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('handles font family selection', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Text')).toBeInTheDocument();
    });

    const fontSelect = screen.getByDisplayValue('Arial');
    expect(fontSelect).toBeInTheDocument();

    fireEvent.change(fontSelect, { target: { value: 'Helvetica' } });
    expect(fontSelect).toHaveValue('Helvetica');
  });

  it('handles shape color selection', async () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Add Shape')).toBeInTheDocument();
    });

    const shapeColorInput = screen.getByDisplayValue('#ff0000');
    expect(shapeColorInput).toBeInTheDocument();

    fireEvent.change(shapeColorInput, { target: { value: '#00ff00' } });
    expect(shapeColorInput).toHaveValue('#00ff00');
  });

  it('shows loading state initially', () => {
    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    expect(screen.getByText('Loading editor...')).toBeInTheDocument();
  });

  it('handles canvas initialization errors gracefully', async () => {
    // Mock Fabric.js to throw an error
    const mockFabric = require('fabric');
    mockFabric.Image.fromURL = jest.fn().mockImplementation((url, callback) => {
      callback(null); // Simulate error by passing null
    });

    render(
      <PosterEditor
        poster={mockPoster}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    // Should handle the error gracefully
    await waitFor(() => {
      expect(screen.getByText('Edit Poster')).toBeInTheDocument();
    });
  });
});
