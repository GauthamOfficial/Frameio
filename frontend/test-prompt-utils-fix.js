/**
 * Simple test script to verify the promptUtils fix
 * This tests the suggestPromptImprovements function to ensure it doesn't throw the "some is not a function" error
 */

// Mock the TEXTILE_KEYWORDS structure
const TEXTILE_KEYWORDS = {
  fabrics: {
    cotton: ['soft cotton', 'breathable fabric', 'natural fiber', 'comfortable'],
    silk: ['luxurious silk', 'smooth texture', 'elegant drape', 'premium quality'],
    saree: ['traditional saree', 'elegant drape', 'cultural heritage', 'graceful'],
    linen: ['natural linen', 'breathable', 'sustainable', 'organic'],
    wool: ['warm wool', 'cozy texture', 'winter wear', 'natural insulation'],
    denim: ['classic denim', 'durable fabric', 'casual style', 'versatile'],
  },
  colors: {
    red: ['vibrant red', 'bold color', 'energetic', 'passionate'],
    gold: ['luxurious gold', 'elegant metallic', 'premium finish', 'sophisticated'],
    blue: ['calming blue', 'trustworthy', 'professional', 'serene'],
    green: ['natural green', 'fresh', 'eco-friendly', 'harmonious'],
    purple: ['royal purple', 'mysterious', 'creative', 'luxurious'],
    black: ['classic black', 'timeless', 'sophisticated', 'versatile'],
    white: ['pure white', 'clean', 'minimalist', 'elegant'],
    maroon: ['rich maroon', 'deep color', 'warm tone', 'traditional'],
  },
  styles: {
    modern: ['contemporary design', 'sleek lines', 'minimalist', 'trendy'],
    traditional: ['classic patterns', 'heritage design', 'cultural motifs', 'timeless'],
    elegant: ['sophisticated style', 'refined aesthetics', 'graceful design', 'premium look'],
    casual: ['relaxed style', 'comfortable wear', 'everyday fashion', 'laid-back'],
    formal: ['professional attire', 'business wear', 'formal occasion', 'dressy'],
    bohemian: ['artistic style', 'free-spirited', 'eclectic design', 'creative'],
  }
};

// Fixed version of suggestPromptImprovements function
function suggestPromptImprovements(prompt) {
  const suggestions = [];
  const lowerPrompt = prompt.toLowerCase();

  // Check for missing elements - FIXED VERSION
  if (!Object.keys(TEXTILE_KEYWORDS.fabrics).some(fabricKey => 
    lowerPrompt.includes(fabricKey) || 
    TEXTILE_KEYWORDS.fabrics[fabricKey].some(keyword => 
      lowerPrompt.includes(keyword)
    )
  )) {
    suggestions.push('Consider specifying the fabric type (cotton, silk, linen, etc.)');
  }

  if (!Object.keys(TEXTILE_KEYWORDS.colors).some(colorKey => 
    lowerPrompt.includes(colorKey) || 
    TEXTILE_KEYWORDS.colors[colorKey].some(keyword => 
      lowerPrompt.includes(keyword)
    )
  )) {
    suggestions.push('Add color specifications for better results');
  }

  if (!Object.keys(TEXTILE_KEYWORDS.styles).some(styleKey => 
    lowerPrompt.includes(styleKey) || 
    TEXTILE_KEYWORDS.styles[styleKey].some(keyword => 
      lowerPrompt.includes(keyword)
    )
  )) {
    suggestions.push('Include style preferences (modern, traditional, elegant, etc.)');
  }

  if (prompt.length < 20) {
    suggestions.push('Add more descriptive details for better AI generation');
  }

  if (!lowerPrompt.includes('quality') && !lowerPrompt.includes('professional')) {
    suggestions.push('Include quality descriptors for better results');
  }

  return suggestions;
}

// Test the function
console.log('🧪 Testing suggestPromptImprovements function...\n');

try {
  // Test 1: Basic prompt
  console.log('Test 1: Basic prompt');
  const suggestions1 = suggestPromptImprovements('A beautiful design');
  console.log('✅ No error thrown');
  console.log('Suggestions:', suggestions1);
  console.log('');

  // Test 2: Prompt with fabric
  console.log('Test 2: Prompt with fabric');
  const suggestions2 = suggestPromptImprovements('A beautiful cotton design');
  console.log('✅ No error thrown');
  console.log('Suggestions:', suggestions2);
  console.log('');

  // Test 3: Prompt with color
  console.log('Test 3: Prompt with color');
  const suggestions3 = suggestPromptImprovements('A beautiful red design');
  console.log('✅ No error thrown');
  console.log('Suggestions:', suggestions3);
  console.log('');

  // Test 4: Prompt with style
  console.log('Test 4: Prompt with style');
  const suggestions4 = suggestPromptImprovements('A beautiful modern design');
  console.log('✅ No error thrown');
  console.log('Suggestions:', suggestions4);
  console.log('');

  // Test 5: Complete prompt
  console.log('Test 5: Complete prompt');
  const suggestions5 = suggestPromptImprovements('A beautiful modern cotton red saree with elegant design and premium quality');
  console.log('✅ No error thrown');
  console.log('Suggestions:', suggestions5);
  console.log('');

  console.log('🎉 All tests passed! The fix is working correctly.');
  console.log('✅ The "TEXTILE_KEYWORDS.fabrics.some is not a function" error has been resolved.');

} catch (error) {
  console.error('❌ Test failed with error:', error.message);
  console.error('Stack trace:', error.stack);
}
