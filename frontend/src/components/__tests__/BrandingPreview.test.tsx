import { render, screen } from '@testing-library/react';
import BrandingPreview from '../BrandingPreview';

// Mock fetch
global.fetch = jest.fn();

describe('BrandingPreview', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('renders loading state initially', () => {
    (fetch as jest.Mock).mockImplementation(() => 
      new Promise(() => {}) // Never resolves to keep loading state
    );

    render(<BrandingPreview />);
    expect(screen.getByText('Branding Preview')).toBeInTheDocument();
  });

  it('renders error state when fetch fails', async () => {
    (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<BrandingPreview />);
    
    // Wait for error to appear
    await screen.findByText('Failed to load company profile');
    expect(screen.getByText('Failed to load company profile')).toBeInTheDocument();
  });

  it('renders incomplete profile state', async () => {
    const mockProfile = {
      company_name: 'Test Company',
      logo: null,
      whatsapp_number: null,
      email: null,
      facebook_link: null,
      has_complete_profile: false,
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    render(<BrandingPreview />);
    
    await screen.findByText('Incomplete Profile');
    expect(screen.getByText('No branding will be added')).toBeInTheDocument();
  });

  it('renders complete profile state', async () => {
    const mockProfile = {
      company_name: 'Test Company',
      logo: 'http://example.com/logo.png',
      whatsapp_number: '+1234567890',
      email: 'test@company.com',
      facebook_link: 'https://facebook.com/company',
      has_complete_profile: true,
    };

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    render(<BrandingPreview />);
    
    await screen.findByText('Complete Profile');
    expect(screen.getByText('✓ Logo will be added to top-right corner')).toBeInTheDocument();
    expect(screen.getByText('✓ Contact info will be added to bottom')).toBeInTheDocument();
  });
});
