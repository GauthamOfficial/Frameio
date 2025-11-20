const axios = require('axios');

async function testGeminiImageGeneration() {
  console.log('🧪 Testing Gemini Image Generation Directly...\n');
  
  const API_BASE_URL = 'http://localhost:8000/api/ai';
  
  try {
    // Test 1: Check service status
    console.log('1️⃣ Checking AI poster service status...');
    const statusResponse = await axios.get(`${API_BASE_URL}/ai-poster/status/`);
    console.log('✅ Status check passed');
    console.log('   Service available:', statusResponse.data.service_available);
    console.log('   Message:', statusResponse.data.message);
    
    // Test 2: Generate a simple poster
    console.log('\n2️⃣ Generating a simple poster...');
    const testData = {
      prompt: 'Simple red circle on white background',
      aspect_ratio: '1:1'
    };
    
    const startTime = Date.now();
    const generateResponse = await axios.post(`${API_BASE_URL}/ai-poster/generate_poster/`, testData, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 120000 // 2 minutes
    });
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    console.log(`✅ Poster generation successful!`);
    console.log(`⏱️  Generation took ${duration.toFixed(2)} seconds`);
    console.log('   Success:', generateResponse.data.success);
    console.log('   Message:', generateResponse.data.message);
    console.log('   Image path:', generateResponse.data.image_path);
    console.log('   Image URL:', generateResponse.data.image_url);
    console.log('   Filename:', generateResponse.data.filename);
    
    // Test 3: Generate another poster with different aspect ratio
    console.log('\n3️⃣ Testing different aspect ratio...');
    const testData2 = {
      prompt: 'Modern textile design with geometric patterns',
      aspect_ratio: '4:5'
    };
    
    const startTime2 = Date.now();
    const generateResponse2 = await axios.post(`${API_BASE_URL}/ai-poster/generate_poster/`, testData2, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 120000
    });
    
    const endTime2 = Date.now();
    const duration2 = (endTime2 - startTime2) / 1000;
    
    console.log(`✅ Second poster generation successful!`);
    console.log(`⏱️  Generation took ${duration2.toFixed(2)} seconds`);
    console.log('   Aspect ratio:', generateResponse2.data.aspect_ratio);
    console.log('   Filename:', generateResponse2.data.filename);
    
    console.log('\n🎉 All Gemini image generation tests passed!');
    console.log('✅ Gemini 2.5 Flash is working correctly for image generation');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
    process.exit(1);
  }
}

// Run the test
testGeminiImageGeneration();
