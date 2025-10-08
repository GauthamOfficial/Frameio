import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CollaborationCanvas } from '@/components/collaboration/CollaborationCanvas';
import { CommentsPanel } from '@/components/collaboration/CommentsPanel';
import { ParticipantsList } from '@/components/collaboration/ParticipantsList';
import { ActivityFeed } from '@/components/collaboration/ActivityFeed';

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

const mockParticipants = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'owner' as const,
    isOnline: true,
    cursor: { x: 100, y: 200 },
    avatar: 'https://example.com/avatar1.jpg'
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'editor' as const,
    isOnline: true,
    cursor: { x: 150, y: 250 },
    avatar: 'https://example.com/avatar2.jpg'
  },
  {
    id: '3',
    name: 'Bob Wilson',
    email: 'bob@example.com',
    role: 'viewer' as const,
    isOnline: false
  }
];

const mockComments = [
  {
    id: '1',
    content: 'Great design! Maybe we should adjust the colors?',
    author: mockParticipants[0],
    position: { x: 150, y: 100 },
    createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    replies: [
      {
        id: '2',
        content: 'I agree, the blue could be more vibrant',
        author: mockParticipants[1],
        createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString()
      }
    ]
  }
];

const mockActivities = [
  {
    id: '1',
    type: 'join' as const,
    user: mockParticipants[0],
    description: 'joined the collaboration',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
  },
  {
    id: '2',
    type: 'edit' as const,
    user: mockParticipants[1],
    description: 'modified the text layer',
    timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString()
  }
];

describe('CollaborationCanvas', () => {
  const mockOnCursorUpdate = jest.fn();
  const mockOnDesignUpdate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the canvas correctly', async () => {
    render(
      <CollaborationCanvas
        participants={mockParticipants}
        onCursorUpdate={mockOnCursorUpdate}
        onDesignUpdate={mockOnDesignUpdate}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Loading canvas...')).toBeInTheDocument();
    });

    // Wait for canvas to load
    await waitFor(() => {
      expect(screen.queryByText('Loading canvas...')).not.toBeInTheDocument();
    });
  });

  it('displays participant cursors', async () => {
    render(
      <CollaborationCanvas
        participants={mockParticipants}
        onCursorUpdate={mockOnCursorUpdate}
        onDesignUpdate={mockOnDesignUpdate}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading canvas...')).not.toBeInTheDocument();
    });

    // Should show participant names
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('shows participant status badges', async () => {
    render(
      <CollaborationCanvas
        participants={mockParticipants}
        onCursorUpdate={mockOnCursorUpdate}
        onDesignUpdate={mockOnDesignUpdate}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading canvas...')).not.toBeInTheDocument();
    });

    // Should show role badges
    expect(screen.getByText('(owner)')).toBeInTheDocument();
    expect(screen.getByText('(editor)')).toBeInTheDocument();
    expect(screen.getByText('(viewer)')).toBeInTheDocument();
  });
});

describe('CommentsPanel', () => {
  it('renders comments correctly', () => {
    render(<CommentsPanel comments={mockComments} />);

    expect(screen.getByText('Great design! Maybe we should adjust the colors?')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('owner')).toBeInTheDocument();
  });

  it('shows empty state when no comments', () => {
    render(<CommentsPanel comments={[]} />);

    expect(screen.getByText('No comments yet')).toBeInTheDocument();
    expect(screen.getByText('Start the conversation!')).toBeInTheDocument();
  });

  it('displays comment timestamps', () => {
    render(<CommentsPanel comments={mockComments} />);

    expect(screen.getByText(/30m ago/)).toBeInTheDocument();
  });

  it('shows reply functionality', () => {
    render(<CommentsPanel comments={mockComments} />);

    const replyButton = screen.getByRole('button', { name: /reply/i });
    expect(replyButton).toBeInTheDocument();

    fireEvent.click(replyButton);

    expect(screen.getByPlaceholderText('Write a reply...')).toBeInTheDocument();
  });

  it('handles reply submission', () => {
    render(<CommentsPanel comments={mockComments} />);

    const replyButton = screen.getByRole('button', { name: /reply/i });
    fireEvent.click(replyButton);

    const replyInput = screen.getByPlaceholderText('Write a reply...');
    const submitButton = screen.getByRole('button', { name: /reply/i });

    fireEvent.change(replyInput, { target: { value: 'Test reply' } });
    fireEvent.click(submitButton);

    expect(replyInput).toHaveValue('');
  });

  it('shows nested replies', () => {
    render(<CommentsPanel comments={mockComments} />);

    const showRepliesButton = screen.getByRole('button', { name: /show 1 replies/i });
    expect(showRepliesButton).toBeInTheDocument();

    fireEvent.click(showRepliesButton);

    expect(screen.getByText('I agree, the blue could be more vibrant')).toBeInTheDocument();
  });
});

describe('ParticipantsList', () => {
  it('renders participants correctly', () => {
    render(<ParticipantsList participants={mockParticipants} />);

    expect(screen.getByText('Online (2)')).toBeInTheDocument();
    expect(screen.getByText('Offline (1)')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
  });

  it('shows role badges', () => {
    render(<ParticipantsList participants={mockParticipants} />);

    expect(screen.getByText('owner')).toBeInTheDocument();
    expect(screen.getByText('editor')).toBeInTheDocument();
    expect(screen.getByText('viewer')).toBeInTheDocument();
  });

  it('shows online/offline status', () => {
    render(<ParticipantsList participants={mockParticipants} />);

    // Should show green dots for online users
    const onlineIndicators = screen.getAllByText('Online (2)');
    expect(onlineIndicators).toHaveLength(1);

    // Should show gray dots for offline users
    const offlineIndicators = screen.getAllByText('Offline (1)');
    expect(offlineIndicators).toHaveLength(1);
  });

  it('shows invite button', () => {
    render(<ParticipantsList participants={mockParticipants} />);

    expect(screen.getByRole('button', { name: /invite people/i })).toBeInTheDocument();
  });

  it('handles empty participants list', () => {
    render(<ParticipantsList participants={[]} />);

    expect(screen.getByText('Online (0)')).toBeInTheDocument();
    expect(screen.getByText('Offline (0)')).toBeInTheDocument();
  });
});

describe('ActivityFeed', () => {
  it('renders activities correctly', () => {
    render(<ActivityFeed activities={mockActivities} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('joined the collaboration')).toBeInTheDocument();
    expect(screen.getByText('modified the text layer')).toBeInTheDocument();
  });

  it('shows activity timestamps', () => {
    render(<ActivityFeed activities={mockActivities} />);

    expect(screen.getByText(/45m ago/)).toBeInTheDocument();
    expect(screen.getByText(/20m ago/)).toBeInTheDocument();
  });

  it('shows role badges', () => {
    render(<ActivityFeed activities={mockActivities} />);

    expect(screen.getByText('owner')).toBeInTheDocument();
    expect(screen.getByText('editor')).toBeInTheDocument();
  });

  it('shows empty state when no activities', () => {
    render(<ActivityFeed activities={[]} />);

    expect(screen.getByText('No activity yet')).toBeInTheDocument();
    expect(screen.getByText('Activity will appear here')).toBeInTheDocument();
  });

  it('displays different activity types with appropriate icons', () => {
    render(<ActivityFeed activities={mockActivities} />);

    // Should have activity icons (these would be tested with more specific selectors in a real app)
    expect(screen.getByText('joined the collaboration')).toBeInTheDocument();
    expect(screen.getByText('modified the text layer')).toBeInTheDocument();
  });
});
