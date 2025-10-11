// Test script to verify the API fix
const testRequest = {
  product_image_url: 'https://example.com/image.jpg',
  fabric_type: 'silk',
  festival: 'diwali',
  price_range: '₹2999',
  style: 'modern',
  custom_text: 'Beautiful silk saree for festive occasions',
  offer_details: 'Special offer available',
  color_palette: ['red', 'gold', 'maroon'],
  generation_type: 'poster'
};

// Simulate the buildEnhancedPrompt function
function buildEnhancedPrompt(request) {
  const parts = [];
  
  // Base description
  if (request.custom_text) {
    parts.push(request.custom_text);
  }
  
  // Fabric type
  if (request.fabric_type) {
    parts.push(`${request.fabric_type} fabric`);
  }
  
  // Style
  if (request.style) {
    parts.push(`${request.style} style`);
  }
  
  // Festival/occasion
  if (request.festival && request.festival !== 'general') {
    parts.push(`for ${request.festival} celebrations`);
  }
  
  // Price range
  if (request.price_range) {
    parts.push(`priced at ${request.price_range}`);
  }
  
  // Color palette
  if (request.color_palette && request.color_palette.length > 0) {
    parts.push(`featuring ${request.color_palette.join(', ')} colors`);
  }
  
  // Offer details
  if (request.offer_details) {
    parts.push(`with ${request.offer_details}`);
  }
  
  // Combine all parts
  let prompt = parts.join(', ');
  
  // Add textile-specific enhancements
  prompt += ', high-quality textile poster design, elegant typography, professional photography style';
  
  return prompt;
}

const enhancedPrompt = buildEnhancedPrompt(testRequest);
console.log('🧪 Testing enhanced prompt generation...');
console.log('Input request:', testRequest);
console.log('Generated prompt:', enhancedPrompt);

const expectedParts = [
  'Beautiful silk saree for festive occasions',
  'silk fabric',
  'modern style',
  'for diwali celebrations',
  'priced at ₹2999',
  'featuring red, gold, maroon colors',
  'with Special offer available',
  'high-quality textile poster design, elegant typography, professional photography style'
];

console.log('\n✅ Enhanced prompt generation test:');
console.log('Expected parts found:', expectedParts.every(part => enhancedPrompt.includes(part)));
console.log('Prompt length:', enhancedPrompt.length);
console.log('Contains textile keywords:', enhancedPrompt.includes('textile') && enhancedPrompt.includes('poster'));
