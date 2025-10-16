/**
 * Business Branding Preview Component
 * Displays company branding information that will be added to generated posters
 */

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Building2, 
  Phone, 
  Mail, 
  Facebook, 
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Eye
} from 'lucide-react'
import { CompanyProfile } from '@/lib/company-profile-service'

interface BusinessBrandingPreviewProps {
  profile: CompanyProfile | null
  hasBrandingData: boolean
  contactInfoText: string
  brandingData: any
  onEditProfile?: () => void
}

export function BusinessBrandingPreview({
  profile,
  hasBrandingData,
  contactInfoText,
  brandingData,
  onEditProfile
}: BusinessBrandingPreviewProps) {
  if (!profile) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Business Branding
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-muted-foreground">No company profile found</p>
            <p className="text-sm text-muted-foreground mt-1">
              Set up your business information to automatically add branding to posters
            </p>
            {onEditProfile && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3"
                onClick={onEditProfile}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Go to Settings
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!hasBrandingData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Business Branding
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <AlertCircle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-muted-foreground">Incomplete business profile</p>
            <p className="text-sm text-muted-foreground mt-1">
              Add your logo and contact details to automatically brand your posters
            </p>
            {onEditProfile && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3"
                onClick={onEditProfile}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Complete Profile
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Business Branding Preview
            <Badge variant="secondary" className="ml-auto">
              <CheckCircle className="h-3 w-3 mr-1" />
              Active
            </Badge>
          </CardTitle>
        </CardHeader>
      <CardContent className="space-y-4">
        {/* Company Name */}
        {profile.company_name && (
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{profile.company_name}</span>
          </div>
        )}

        {/* Logo Preview */}
        {brandingData?.logo_url && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Company Logo</span>
            </div>
            <div className="border rounded-lg p-2 bg-muted/50">
              <img 
                src={brandingData.logo_url} 
                alt="Company Logo" 
                className="h-12 w-auto object-contain mx-auto"
              />
            </div>
          </div>
        )}

        {/* Contact Information */}
        {contactInfoText && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Contact Information</span>
            </div>
            <div className="bg-muted/50 rounded-lg p-3">
              <pre className="text-xs whitespace-pre-wrap font-mono">
                {contactInfoText}
              </pre>
            </div>
          </div>
        )}

        {/* Brand Colors */}
        {brandingData?.brand_colors && brandingData.brand_colors.length > 0 && (
          <div className="space-y-2">
            <span className="text-sm font-medium">Brand Colors</span>
            <div className="flex gap-2">
              {brandingData.brand_colors.map((color: string, index: number) => (
                <div
                  key={index}
                  className="w-6 h-6 rounded-full border"
                  style={{ backgroundColor: color }}
                  title={color}
                />
              ))}
            </div>
          </div>
        )}

        {/* Visual Preview */}
        <div className="space-y-4">
          <h4 className="font-medium text-sm">How Your Branding Will Appear:</h4>
          
          {/* Logo Preview */}
          {brandingData?.logo_url && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ImageIcon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Company Logo</span>
                <Badge variant="outline" className="text-xs">
                  {profile.preferred_logo_position?.replace('_', ' ')}
                </Badge>
              </div>
              <div className="border rounded-lg p-3 bg-muted/50">
                <div className="flex justify-center">
                  <img 
                    src={brandingData.logo_url} 
                    alt="Company Logo" 
                    className="h-16 w-auto object-contain"
                  />
                </div>
                <p className="text-xs text-center text-muted-foreground mt-2">
                  Logo will be positioned at {profile.preferred_logo_position?.replace('_', ' ')}
                </p>
              </div>
            </div>
          )}

          {/* Contact Information Preview */}
          {contactInfoText && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Contact Information</span>
                <Badge variant="outline" className="text-xs">Bottom overlay</Badge>
              </div>
              <div className="bg-gray-900 text-white rounded-lg p-3 text-sm">
                <div className="space-y-1">
                  {contactInfoText.split('\n').map((line, index) => (
                    <div key={index} className="flex items-center gap-2">
                      {line}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-300 mt-2">
                  Contact info will appear as a semi-transparent overlay at the bottom
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Preview Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium text-blue-900">Auto-Branding Enabled</p>
              <p className="text-blue-700 mt-1">
                Your logo and contact information will be automatically added to generated posters.
              </p>
            </div>
          </div>
        </div>

        {/* Edit Button */}
        {onEditProfile && (
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full"
            onClick={onEditProfile}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Edit Business Profile
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
