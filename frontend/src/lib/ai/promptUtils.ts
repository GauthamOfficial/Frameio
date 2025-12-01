/**
 * AI Prompt Engineering Utilities for Textile Themes
 * Generates optimized prompts for textile marketing content
 */

export interface TextilePromptParams {
  theme: string;
  color?: string;
  style?: string;
  fabric?: string;
  occasion?: string;
  mood?: string;
  additionalKeywords?: string[];
}

export interface GeneratedPrompt {
  prompt: string;
  enhancedPrompt: string;
  keywords: string[];
  metadata: {
    theme: string;
    style: string;
    colorScheme: string;
    generated_at: string;
  };
}

// Textile-specific keyword mappings
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
    elegant: ['sophisticated style', 'refined aesthetics', 'luxury appeal', 'graceful'],
    casual: ['relaxed fit', 'everyday wear', 'comfortable', 'versatile'],
    festive: ['celebration wear', 'special occasion', 'vibrant colors', 'joyful'],
    minimalist: ['clean design', 'simple patterns', 'uncluttered', 'focused'],
    bohemian: ['free-spirited', 'artistic', 'eclectic', 'creative'],
  },
  occasions: {
    wedding: ['bridal wear', 'ceremonial', 'special celebration', 'memorable occasion'],
    festival: ['festive celebration', 'cultural event', 'traditional gathering', 'joyful occasion'],
    casual: ['everyday wear', 'comfortable', 'relaxed setting', 'daily use'],
    formal: ['business attire', 'professional setting', 'corporate', 'sophisticated'],
    party: ['social gathering', 'entertainment', 'fun occasion', 'celebration'],
  },
  moods: {
    joyful: ['happy', 'cheerful', 'uplifting', 'positive energy'],
    elegant: ['sophisticated', 'refined', 'graceful', 'classy'],
    vibrant: ['energetic', 'bold', 'dynamic', 'eye-catching'],
    calm: ['peaceful', 'serene', 'relaxing', 'tranquil'],
    luxurious: ['premium', 'high-end', 'exclusive', 'opulent'],
    cozy: ['comfortable', 'warm', 'inviting', 'snug'],
  },
};

// Template prompts for different textile categories
const PROMPT_TEMPLATES = {
  saree: 'Create a stunning {style} saree design featuring {color} {fabric} with {mood} aesthetic, perfect for {occasion}. Include elegant draping, traditional patterns, and {additionalKeywords}.',
  cotton: 'Design a {style} cotton textile collection with {color} color scheme, emphasizing {mood} feel and {occasion} suitability. Focus on breathable fabric, natural texture, and {additionalKeywords}.',
  silk: 'Craft a luxurious {style} silk design in {color} tones, showcasing {mood} elegance for {occasion}. Highlight smooth texture, premium quality, and {additionalKeywords}.',
  general: 'Create a {style} textile design featuring {color} {fabric} with {mood} characteristics, ideal for {occasion}. Emphasize quality, comfort, and {additionalKeywords}.',
};

/**
 * Generate a textile-aware prompt
 */
export function generateTextilePrompt(params: TextilePromptParams): GeneratedPrompt {
  const {
    theme,
    color = 'neutral',
    style = 'modern',
    fabric = 'cotton',
    occasion = 'casual',
    mood = 'elegant',
    additionalKeywords = [],
  } = params;

  // Get relevant keywords for each category
  const fabricKeywords = TEXTILE_KEYWORDS.fabrics[fabric as keyof typeof TEXTILE_KEYWORDS.fabrics] || [];
  const colorKeywords = TEXTILE_KEYWORDS.colors[color as keyof typeof TEXTILE_KEYWORDS.colors] || [];
  const styleKeywords = TEXTILE_KEYWORDS.styles[style as keyof typeof TEXTILE_KEYWORDS.styles] || [];
  const occasionKeywords = TEXTILE_KEYWORDS.occasions[occasion as keyof typeof TEXTILE_KEYWORDS.occasions] || [];
  const moodKeywords = TEXTILE_KEYWORDS.moods[mood as keyof typeof TEXTILE_KEYWORDS.moods] || [];

  // Combine all keywords
  const allKeywords = [
    ...fabricKeywords,
    ...colorKeywords,
    ...styleKeywords,
    ...occasionKeywords,
    ...moodKeywords,
    ...additionalKeywords,
  ];

  // Select template based on fabric type
  const template = PROMPT_TEMPLATES[fabric as keyof typeof PROMPT_TEMPLATES] || PROMPT_TEMPLATES.general;

  // Generate the prompt
  const basePrompt = template
    .replace('{style}', style)
    .replace('{color}', color)
    .replace('{fabric}', fabric)
    .replace('{mood}', mood)
    .replace('{occasion}', occasion)
    .replace('{additionalKeywords}', additionalKeywords.slice(0, 3).join(', '));

  // Enhance with additional context
  const enhancedPrompt = `${basePrompt} High-quality textile photography, professional lighting, commercial-grade image, detailed fabric texture, vibrant colors, marketing-ready poster design.`;

  return {
    prompt: basePrompt,
    enhancedPrompt,
    keywords: allKeywords,
    metadata: {
      theme,
      style,
      colorScheme: color,
      generated_at: new Date().toISOString(),
    },
  };
}

/**
 * Generate multiple prompt variations
 */
export function generatePromptVariations(params: TextilePromptParams, count: number = 3): GeneratedPrompt[] {
  const variations: GeneratedPrompt[] = [];
  const baseParams = { ...params };

  // Generate variations by modifying different aspects
  for (let i = 0; i < count; i++) {
    const variationParams = { ...baseParams };
    
    // Modify style for variation
    if (i === 1) {
      variationParams.style = variationParams.style === 'modern' ? 'traditional' : 'modern';
    }
    
    // Modify mood for variation
    if (i === 2) {
      variationParams.mood = variationParams.mood === 'elegant' ? 'vibrant' : 'elegant';
    }

    variations.push(generateTextilePrompt(variationParams));
  }

  return variations;
}

/**
 * Extract keywords from user input
 */
export function extractKeywordsFromInput(input: string): {
  theme: string;
  colors: string[];
  styles: string[];
  fabrics: string[];
} {
  const lowerInput = input.toLowerCase();
  
  const colors = Object.keys(TEXTILE_KEYWORDS.colors).filter(color => 
    lowerInput.includes(color)
  );
  
  const styles = Object.keys(TEXTILE_KEYWORDS.styles).filter(style => 
    lowerInput.includes(style)
  );
  
  const fabrics = Object.keys(TEXTILE_KEYWORDS.fabrics).filter(fabric => 
    lowerInput.includes(fabric)
  );

  // Extract theme (first few words or common textile terms)
  const textileTerms = ['saree', 'dress', 'shirt', 'pants', 'collection', 'design', 'pattern'];
  const themeWords = input.split(' ').filter(word => 
    textileTerms.some(term => word.toLowerCase().includes(term)) ||
    word.length > 3
  );
  
  const theme = themeWords.slice(0, 3).join(' ') || 'textile design';

  return {
    theme,
    colors,
    styles,
    fabrics,
  };
}

/**
 * Suggest prompt improvements
 */
export function suggestPromptImprovements(prompt: string): string[] {
  const suggestions: string[] = [];
  const lowerPrompt = prompt.toLowerCase();

  // Check for missing elements
  if (!Object.keys(TEXTILE_KEYWORDS.fabrics).some(fabricKey => 
    lowerPrompt.includes(fabricKey) || 
    TEXTILE_KEYWORDS.fabrics[fabricKey as keyof typeof TEXTILE_KEYWORDS.fabrics].some(keyword => 
      lowerPrompt.includes(keyword)
    )
  )) {
    suggestions.push('Consider specifying the fabric type (cotton, silk, linen, etc.)');
  }

  if (!Object.keys(TEXTILE_KEYWORDS.colors).some(colorKey => 
    lowerPrompt.includes(colorKey) || 
    TEXTILE_KEYWORDS.colors[colorKey as keyof typeof TEXTILE_KEYWORDS.colors].some(keyword => 
      lowerPrompt.includes(keyword)
    )
  )) {
    suggestions.push('Add color specifications for better results');
  }

  if (!Object.keys(TEXTILE_KEYWORDS.styles).some(styleKey => 
    lowerPrompt.includes(styleKey) || 
    TEXTILE_KEYWORDS.styles[styleKey as keyof typeof TEXTILE_KEYWORDS.styles].some(keyword => 
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

/**
 * Validate prompt quality
 */
export function validatePrompt(prompt: string): {
  isValid: boolean;
  score: number;
  issues: string[];
} {
  const issues: string[] = [];
  let score = 0;

  // Length check
  if (prompt.length < 10) {
    issues.push('Prompt is too short');
    score -= 2;
  } else if (prompt.length > 500) {
    issues.push('Prompt is too long');
    score -= 1;
  } else {
    score += 1;
  }

  // Textile relevance check
  const textileTerms = ['textile', 'fabric', 'cloth', 'saree', 'cotton', 'silk', 'design', 'pattern'];
  const hasTextileTerms = textileTerms.some(term => prompt.toLowerCase().includes(term));
  
  if (!hasTextileTerms) {
    issues.push('Prompt lacks textile-specific terms');
    score -= 2;
  } else {
    score += 2;
  }

  // Quality descriptors check
  const qualityTerms = ['high quality', 'professional', 'detailed', 'vibrant', 'elegant'];
  const hasQualityTerms = qualityTerms.some(term => prompt.toLowerCase().includes(term));
  
  if (!hasQualityTerms) {
    issues.push('Consider adding quality descriptors');
    score -= 1;
  } else {
    score += 1;
  }

  return {
    isValid: issues.length === 0,
    score: Math.max(0, score),
    issues,
  };
}
