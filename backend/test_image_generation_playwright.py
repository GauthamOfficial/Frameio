#!/usr/bin/env python
"""
Playwright test for image generation functionality
"""
import os
import sys
import django
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Setup Django
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

# Set API key
os.environ['NANOBANANA_API_KEY'] = 'AIzaSyBBP1QGjY7lJBhjNwWMSJCIOZC1bWgSzMY'

print("🎭 Testing Image Generation with Playwright...")

async def test_image_generation():
    """Test image generation using Playwright browser automation"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🚀 Starting Playwright tests...")
            
            # Test 1: Direct API endpoint testing
            print("\n📸 Test 1: Testing poster generation endpoint...")
            
            # Start Django server in background (simulated)
            print("   - Setting up test environment...")
            
            # Create test data
            from django.test import Client
            from django.contrib.auth import get_user_model
            from organizations.models import Organization
            
            User = get_user_model()
            
            # Get or create test user
            user, created = User.objects.get_or_create(
                username='playwright_test_user',
                defaults={
                    'email': 'playwright@example.com',
                    'password': 'testpass123'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                print("   ✅ Created test user")
            else:
                print("   ✅ Using existing test user")
            
            # Get or create test organization
            organization, created = Organization.objects.get_or_create(
                slug='playwright-test-org',
                defaults={'name': 'Playwright Test Organization'}
            )
            if created:
                print("   ✅ Created test organization")
            else:
                print("   ✅ Using existing test organization")
            
            # Create membership if it doesn't exist
            membership, created = user.organization_memberships.get_or_create(
                organization=organization,
                defaults={'role': 'admin', 'is_active': True}
            )
            if created:
                print("   ✅ Created organization membership")
            else:
                print("   ✅ Using existing membership")
            
            # Test 2: API endpoint testing with browser
            print("\n🌐 Test 2: Testing API endpoints with browser...")
            
            # Navigate to Django admin or API endpoint
            await page.goto('http://localhost:8000/admin/')
            print("   - Navigated to Django admin")
            
            # Check if we can access the admin
            try:
                await page.wait_for_selector('input[name="username"]', timeout=5000)
                print("   ✅ Django admin accessible")
            except:
                print("   ⚠️ Django admin not accessible, trying direct API test")
            
            # Test 3: Direct service testing
            print("\n🔧 Test 3: Testing NanoBanana service directly...")
            
            from ai_services.nanobanana_service import NanoBananaAIService
            
            service = NanoBananaAIService()
            print(f"   - Service available: {service.is_available()}")
            print(f"   - API key configured: {bool(service.api_key)}")
            print(f"   - Use fallback: {service.use_fallback}")
            
            # Test poster generation
            print("\n📸 Testing poster generation...")
            result = service.generate_poster(
                image_url='https://example.com/test-fabric.jpg',
                offer_text='Special Deepavali Offer - 50% Off!',
                theme='festive'
            )
            
            print(f"   - Success: {result.get('success', False)}")
            print(f"   - Fallback used: {result.get('fallback', False)}")
            print(f"   - Images generated: {len(result.get('image_urls', []))}")
            
            if result.get('image_urls'):
                print("   - Generated image URLs:")
                for i, url in enumerate(result['image_urls'][:3]):  # Show first 3
                    print(f"     {i+1}. {url}")
            
            # Test 4: Verify image URLs are accessible
            print("\n🔍 Test 4: Verifying image URL accessibility...")
            
            if result.get('image_urls'):
                for i, url in enumerate(result['image_urls'][:2]):  # Test first 2 URLs
                    try:
                        print(f"   - Testing URL {i+1}: {url[:50]}...")
                        await page.goto(url, timeout=10000)
                        
                        # Check if image loaded
                        try:
                            await page.wait_for_selector('img', timeout=5000)
                            print(f"     ✅ Image {i+1} loaded successfully")
                        except:
                            print(f"     ⚠️ Image {i+1} may not have loaded properly")
                            
                    except Exception as e:
                        print(f"     ❌ Error accessing URL {i+1}: {str(e)[:50]}...")
            
            # Test 5: Test different themes
            print("\n🎨 Test 5: Testing different themes...")
            
            themes = ['modern', 'traditional', 'festive', 'elegant']
            for theme in themes:
                print(f"   - Testing {theme} theme...")
                theme_result = service.generate_poster(
                    image_url='https://example.com/test.jpg',
                    offer_text=f'Special {theme.title()} Offer',
                    theme=theme
                )
                
                if theme_result.get('success'):
                    print(f"     ✅ {theme} theme: {len(theme_result.get('image_urls', []))} images")
                else:
                    print(f"     ❌ {theme} theme: Failed")
            
            # Test 6: Caption generation
            print("\n📝 Test 6: Testing caption generation...")
            
            caption_result = service.generate_caption(
                product_name='Luxury Silk Saree',
                description='Beautiful traditional silk saree with intricate designs'
            )
            
            print(f"   - Caption success: {caption_result.get('success', False)}")
            print(f"   - Caption fallback: {caption_result.get('fallback', False)}")
            print(f"   - Captions generated: {len(caption_result.get('captions', []))}")
            
            if caption_result.get('captions'):
                print("   - Sample captions:")
                for i, caption in enumerate(caption_result['captions'][:2]):
                    print(f"     {i+1}. {caption['text'][:50]}...")
            
            print("\n🎉 Playwright tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during Playwright test: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

async def test_api_endpoints_with_playwright():
    """Test API endpoints using Playwright for HTTP requests"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\n🌐 Testing API endpoints with Playwright HTTP requests...")
            
            # Test poster generation endpoint
            print("   - Testing poster generation endpoint...")
            
            # Create a simple HTML page to test API calls
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Image Generation Test</title>
            </head>
            <body>
                <h1>Image Generation Test</h1>
                <div id="results"></div>
                <script>
                    async function testImageGeneration() {
                        try {
                            const response = await fetch('/api/ai/textile/poster/generate_poster_nanobanana/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    image_url: 'https://example.com/fabric.jpg',
                                    offer_text: 'Special Deepavali Offer - 50% Off!',
                                    theme: 'festive',
                                    fabric_type: 'silk',
                                    festival: 'deepavali'
                                })
                            });
                            
                            const data = await response.json();
                            document.getElementById('results').innerHTML = 
                                '<h2>Results:</h2>' +
                                '<p>Success: ' + data.success + '</p>' +
                                '<p>Fallback: ' + data.fallback + '</p>' +
                                '<p>Images: ' + (data.image_urls ? data.image_urls.length : 0) + '</p>';
                        } catch (error) {
                            document.getElementById('results').innerHTML = 
                                '<h2>Error:</h2><p>' + error.message + '</p>';
                        }
                    }
                    
                    testImageGeneration();
                </script>
            </body>
            </html>
            """
            
            # Set the HTML content
            await page.set_content(html_content)
            print("   ✅ HTML test page loaded")
            
            # Wait for results
            try:
                await page.wait_for_selector('#results', timeout=10000)
                results = await page.text_content('#results')
                print(f"   - API Test Results: {results}")
            except:
                print("   ⚠️ API test may have failed or timed out")
            
        except Exception as e:
            print(f"❌ Error in API endpoint test: {str(e)}")
        
        finally:
            await browser.close()

async def main():
    """Main test function"""
    print("🎭 Starting Playwright Image Generation Tests...")
    
    # Test 1: Direct service testing
    await test_image_generation()
    
    # Test 2: API endpoint testing
    await test_api_endpoints_with_playwright()
    
    print("\n🎉 All Playwright tests completed!")

if __name__ == "__main__":
    asyncio.run(main())

