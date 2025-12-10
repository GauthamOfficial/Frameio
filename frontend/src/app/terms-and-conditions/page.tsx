"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Footer } from "@/components/layout/footer"
import { Logo } from "@/components/common/logo"
import Link from "next/link"

export default function TermsAndConditionsPage() {
  return (
    <div className="min-h-screen bg-background fabric-texture">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Logo href="/" />

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link
                href="/"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Home
              </Link>
              <Link
                href="/about"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Contact Us
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Page Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Terms & Conditions
            </h1>
            <p className="text-lg text-muted-foreground">
              Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          {/* Agreement Summary */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Agreement Summary</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                These Terms and Conditions (&quot;Terms&quot;) govern your access to and use of Frameio (&quot;Service&quot;), operated by Frameio (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;). By accessing or using our Service, you agree to be bound by these Terms. If you disagree with any part of these Terms, you may not access the Service.
              </p>
              <p className="text-foreground leading-relaxed mt-4">
                These Terms constitute a legally binding agreement between you and Frameio. Please read them carefully before using our platform.
              </p>
            </CardContent>
          </Card>

          {/* Eligibility */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Eligibility</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                To use Frameio, you must:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Be at least 18 years of age or have parental/guardian consent</li>
                <li>Have the legal capacity to enter into binding agreements</li>
                <li>Provide accurate, current, and complete information during registration</li>
                <li>Maintain the security of your account credentials</li>
                <li>Comply with all applicable laws and regulations</li>
                <li>Not be prohibited from using the Service under applicable law</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                You are responsible for all activities that occur under your account, whether authorized by you or not.
              </p>
            </CardContent>
          </Card>

          {/* Acceptable Use Rules */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Acceptable Use Rules</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                When using Frameio, you agree to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Use the Service only for lawful purposes and in accordance with these Terms</li>
                <li>Provide accurate and truthful information when creating content</li>
                <li>Respect intellectual property rights of others</li>
                <li>Maintain the confidentiality of your account information</li>
                <li>Use the Service in a manner that does not interfere with or disrupt the platform</li>
                <li>Report any security vulnerabilities or breaches to us immediately</li>
                <li>Comply with all applicable local, state, national, and international laws</li>
              </ul>
            </CardContent>
          </Card>

          {/* Prohibited Actions */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Prohibited Actions</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                You are strictly prohibited from:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Using the Service to create content that is illegal, harmful, or violates any laws</li>
                <li>Uploading or generating content that infringes on intellectual property rights</li>
                <li>Creating content that is defamatory, libelous, or violates privacy rights</li>
                <li>Generating content that promotes hate speech, discrimination, or violence</li>
                <li>Attempting to reverse engineer, decompile, or extract source code from the Service</li>
                <li>Using automated systems (bots, scrapers) to access the Service without permission</li>
                <li>Sharing your account credentials with others or creating multiple accounts to circumvent usage limits</li>
                <li>Interfering with or disrupting the Service&apos;s security, servers, or networks</li>
                <li>Using the Service to transmit viruses, malware, or other harmful code</li>
                <li>Impersonating any person or entity or misrepresenting your affiliation</li>
              </ul>
            </CardContent>
          </Card>

          {/* AI-Generated Content Rules */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">AI-Generated Content Rules</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                Frameio uses artificial intelligence to generate poster designs. By using our Service, you acknowledge and agree that:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>AI-generated content may not always be perfect and may require review and editing</li>
                <li>You are responsible for reviewing and approving all AI-generated content before use</li>
                <li>AI-generated content should not be used in ways that mislead or deceive others</li>
                <li>You must ensure AI-generated content complies with all applicable laws and regulations</li>
                <li>We do not guarantee the accuracy, completeness, or suitability of AI-generated content</li>
                <li>You should not rely solely on AI-generated content for critical business decisions without human review</li>
                <li>AI models may produce similar or identical outputs for different users</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                You are solely responsible for the final content you create and publish using our Service.
              </p>
            </CardContent>
          </Card>

          {/* Intellectual Property */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Intellectual Property</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <h3 className="text-lg font-semibold text-foreground mb-3">Service Ownership</h3>
              <p className="text-foreground leading-relaxed mb-4">
                The Service, including its original content, features, and functionality, is owned by Frameio and protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.
              </p>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">User-Generated Content</h3>
              <p className="text-foreground leading-relaxed mb-4">
                You retain ownership of content you create using our Service. However, by using Frameio, you grant us a worldwide, non-exclusive, royalty-free license to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Use, store, and process your content to provide and improve the Service</li>
                <li>Display your content on the platform for your use</li>
                <li>Use anonymized, aggregated data for analytics and service improvement</li>
              </ul>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">Third-Party Content</h3>
              <p className="text-foreground leading-relaxed">
                You are responsible for ensuring that any content you upload or use does not infringe on third-party intellectual property rights. You must obtain all necessary permissions and licenses before using copyrighted material.
              </p>
            </CardContent>
          </Card>

          {/* Payments & Refunds */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Payments & Refunds</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <h3 className="text-lg font-semibold text-foreground mb-3">Payment Terms</h3>
              <p className="text-foreground leading-relaxed mb-4">
                Frameio may offer paid subscription plans or pay-per-use services. By purchasing a subscription or making a payment, you agree to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Pay all fees associated with your chosen plan</li>
                <li>Provide accurate payment information</li>
                <li>Authorize us to charge your payment method for recurring subscriptions</li>
                <li>Understand that prices may change with reasonable notice</li>
              </ul>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">Refund Policy</h3>
              <p className="text-foreground leading-relaxed">
                Refund policies will be specified at the time of purchase. Generally, refunds may be available for:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground mt-2">
                <li>Service failures or technical issues preventing use</li>
                <li>Duplicate charges or billing errors</li>
                <li>As otherwise required by applicable law</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                To request a refund, please contact us using the information provided in the Contact section.
              </p>
            </CardContent>
          </Card>

          {/* Termination */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Termination</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <h3 className="text-lg font-semibold text-foreground mb-3">Termination by You</h3>
              <p className="text-foreground leading-relaxed mb-4">
                You may terminate your account at any time by contacting us or using account deletion features in your settings.
              </p>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">Termination by Us</h3>
              <p className="text-foreground leading-relaxed mb-4">
                We reserve the right to suspend or terminate your account immediately, without prior notice, if you:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Violate these Terms or any applicable laws</li>
                <li>Engage in fraudulent, abusive, or illegal activity</li>
                <li>Fail to pay required fees</li>
                <li>Use the Service in a manner that harms us or other users</li>
              </ul>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">Effect of Termination</h3>
              <p className="text-foreground leading-relaxed">
                Upon termination, your right to use the Service will immediately cease. We may delete your account data in accordance with our Privacy Policy. Provisions that by their nature should survive termination will remain in effect.
              </p>
            </CardContent>
          </Card>

          {/* Limitation of Liability */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Limitation of Liability</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Frameio is provided &quot;AS IS&quot; and &quot;AS AVAILABLE&quot; without warranties of any kind</li>
                <li>We do not guarantee that the Service will be uninterrupted, error-free, or secure</li>
                <li>We are not liable for any indirect, incidental, special, consequential, or punitive damages</li>
                <li>Our total liability shall not exceed the amount you paid us in the 12 months preceding the claim</li>
                <li>We are not responsible for content created by users or AI-generated content</li>
                <li>We do not warrant the accuracy, completeness, or usefulness of any information on the Service</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                Some jurisdictions do not allow the exclusion of certain warranties or limitations of liability, so some of the above limitations may not apply to you.
              </p>
            </CardContent>
          </Card>

          {/* Governing Law */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Governing Law</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                These Terms shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to its conflict of law provisions. Any disputes arising from or relating to these Terms or the Service shall be subject to the exclusive jurisdiction of the courts located in [Your Jurisdiction].
              </p>
              <p className="text-foreground leading-relaxed mt-4">
                If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary, and the remaining provisions shall remain in full force and effect.
              </p>
            </CardContent>
          </Card>

          {/* Contact Section */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Contact</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                If you have any questions about these Terms & Conditions, please contact us:
              </p>
              <div className="space-y-2 text-foreground">
                <p><strong>Email:</strong> <a href="mailto:startuptsg@gmail.com" className="text-[#8B2635] hover:underline">startuptsg@gmail.com</a></p>
                <p><strong>Phone:</strong> <a href="tel:0759819250" className="text-[#8B2635] hover:underline">0759819250</a></p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

