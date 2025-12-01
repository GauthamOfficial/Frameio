/**
 * Tests for promptUtils.ts
 * Verifies the fix for TEXTILE_KEYWORDS.some() error
 */

import { suggestPromptImprovements } from '../promptUtils';

describe('promptUtils', () => {
  describe('suggestPromptImprovements', () => {
    it('should not throw error when checking for fabric keywords', () => {
      const prompt = 'A beautiful design';
      
      // This should not throw the "TEXTILE_KEYWORDS.fabrics.some is not a function" error
      expect(() => {
        const suggestions = suggestPromptImprovements(prompt);
        expect(Array.isArray(suggestions)).toBe(true);
      }).not.toThrow();
    });

    it('should suggest fabric type when not specified', () => {
      const prompt = 'A beautiful design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).toContain('Consider specifying the fabric type (cotton, silk, linen, etc.)');
    });

    it('should suggest color specifications when not specified', () => {
      const prompt = 'A beautiful design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).toContain('Add color specifications for better results');
    });

    it('should suggest style preferences when not specified', () => {
      const prompt = 'A beautiful design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).toContain('Include style preferences (modern, traditional, elegant, etc.)');
    });

    it('should not suggest fabric type when cotton is mentioned', () => {
      const prompt = 'A beautiful cotton design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).not.toContain('Consider specifying the fabric type (cotton, silk, linen, etc.)');
    });

    it('should not suggest color when red is mentioned', () => {
      const prompt = 'A beautiful red design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).not.toContain('Add color specifications for better results');
    });

    it('should not suggest style when modern is mentioned', () => {
      const prompt = 'A beautiful modern design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).not.toContain('Include style preferences (modern, traditional, elegant, etc.)');
    });

    it('should suggest more details for short prompts', () => {
      const prompt = 'Design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).toContain('Add more descriptive details for better AI generation');
    });

    it('should suggest quality descriptors when not present', () => {
      const prompt = 'A beautiful design';
      const suggestions = suggestPromptImprovements(prompt);
      
      expect(suggestions).toContain('Include quality descriptors for better results');
    });
  });
});
