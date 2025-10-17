'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertCircle, Building2 } from 'lucide-react';
import Image from 'next/image';

interface CompanyProfile {
  company_name: string;
  logo: string | null;
  whatsapp_number: string | null;
  email: string | null;
  facebook_link: string | null;
  has_complete_profile: boolean;
}

interface BrandingPreviewProps {
  className?: string;
}

export default function BrandingPreview({ className }: BrandingPreviewProps) {
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  console.log('BrandingPreview component rendered');

  useEffect(() => {
    fetchCompanyProfile();
  }, []);

  const fetchCompanyProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get company profile from the backend
      const response = await fetch('http://localhost:8000/api/users/company-profiles/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCompanyProfile(data);
      } else {
        // If no company profile found, create a mock for demonstration
        console.log('No company profile found, using mock data');
        setCompanyProfile({
          company_name: 'Your Company Name',
          logo: null,
          whatsapp_number: '+1234567890',
          email: 'contact@yourcompany.com',
          facebook_link: 'https://facebook.com/yourcompany',
          has_complete_profile: false,
        });
      }
    } catch (err) {
      console.error('Error fetching company profile:', err);
      setError('Failed to load company profile');
      
      // Fallback to mock data
      setCompanyProfile({
        company_name: 'Your Company Name',
        logo: null,
        whatsapp_number: '+1234567890',
        email: 'contact@yourcompany.com',
        facebook_link: 'https://facebook.com/yourcompany',
        has_complete_profile: false,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Branding Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Branding Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const contactInfo = [];
  if (companyProfile?.whatsapp_number) {
    contactInfo.push({ type: 'whatsapp', value: companyProfile.whatsapp_number });
  }
  if (companyProfile?.email) {
    contactInfo.push({ type: 'email', value: companyProfile.email });
  }
  if (companyProfile?.facebook_link) {
    contactInfo.push({ type: 'facebook', value: companyProfile.facebook_link });
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-4 w-4" />
          Branding Preview
          {companyProfile?.has_complete_profile ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-500" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Profile Status */}
        <div className="flex items-center gap-2">
          <Badge variant={companyProfile?.has_complete_profile ? "default" : "secondary"}>
            {companyProfile?.has_complete_profile ? "Complete Profile" : "Incomplete Profile"}
          </Badge>
        </div>

        {/* Company Name */}
        {companyProfile?.company_name && (
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium">{companyProfile.company_name}</span>
          </div>
        )}

        {/* Logo Preview */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Logo:</h4>
          {companyProfile?.logo ? (
            <div className="flex items-center gap-2">
              <img 
                src={companyProfile.logo} 
                alt="Company Logo" 
                className="w-12 h-12 object-contain border rounded"
              />
              <span className="text-sm text-green-600">✓ Logo uploaded</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-yellow-600">
              <AlertCircle className="h-4 w-4" />
              <span>No logo uploaded</span>
            </div>
          )}
        </div>

        {/* Contact Information */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-white">Contact Information:</h4>
          <div className="space-y-1">
            {contactInfo.length > 0 ? (
              contactInfo.map((contact, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  {contact.type === 'whatsapp' && (
                    <Image 
                      src="/WhatsApp.svg" 
                      alt="WhatsApp" 
                      width={16} 
                      height={16} 
                      className="text-green-500"
                    />
                  )}
                  {contact.type === 'email' && (
                    <Image 
                      src="/Email.svg" 
                      alt="Email" 
                      width={16} 
                      height={16} 
                      className="text-blue-500"
                    />
                  )}
                  {contact.type === 'facebook' && (
                    <Image 
                      src="/Facebook.svg" 
                      alt="Facebook" 
                      width={16} 
                      height={16} 
                      className="text-blue-600"
                    />
                  )}
                  <span className="text-white">{contact.value}</span>
                </div>
              ))
            ) : (
              <div className="flex items-center gap-2 text-sm text-yellow-600">
                <AlertCircle className="h-4 w-4" />
                <span>No contact information</span>
              </div>
            )}
          </div>
        </div>

        {/* Branding Status */}
        <div className="p-3 bg-gray-50 rounded-md">
          <h4 className="text-sm font-medium text-gray-700 mb-2">What will be added to your poster:</h4>
          {companyProfile?.has_complete_profile ? (
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-3 w-3" />
                <span>✓ Logo at top-right corner</span>
              </div>
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-3 w-3" />
                <span>✓ Contact info at bottom with background</span>
              </div>
              <div className="text-xs text-gray-500 mt-2 p-2 bg-white rounded border">
                <strong>Preview:</strong><br/>
                • Logo: {companyProfile.company_name} (top-right)<br/>
                • Contact: {contactInfo.length > 0 ? contactInfo.map(c => c.value).join(', ') : 'None'}
              </div>
            </div>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-yellow-600">
                <AlertCircle className="h-3 w-3" />
                <span>⚠️ No branding will be added</span>
              </div>
              <div className="text-xs text-gray-500 mt-2 p-2 bg-white rounded border">
                <strong>Missing:</strong><br/>
                {!companyProfile?.logo && '• Logo upload required<br/>'}
                {contactInfo.length === 0 && '• Contact information required<br/>'}
                Complete your company profile to enable automatic branding.
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
