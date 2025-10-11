// Fix for the URL validation issue in enhanced-poster-generator.tsx
// Replace the URL validation section (around lines 278-287) with this:

    // Handle both relative and absolute URLs
    let finalImageUrl = data.poster_url

    // If it's a relative URL, make it absolute
    if (data.poster_url.startsWith('/')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      finalImageUrl = `${baseUrl}${data.poster_url}`
      console.log('🔗 Converted relative URL to absolute:', finalImageUrl)
    }

    // Validate the final URL
    try {
      new URL(finalImageUrl)
    } catch (urlError) {
      console.error('❌ Invalid poster URL format:', finalImageUrl)
      setGenerationError('Invalid image URL generated. Please try again.')
      setAiServiceStatus('error')
      showError('Invalid image URL generated. Please try again.')
      return
    }

// And then update the posterData to use finalImageUrl instead of data.poster_url:

    const posterData = {
      url: finalImageUrl, // Use the processed URL instead of data.poster_url
      captions: data.caption_suggestions?.length > 0 ? data.caption_suggestions : dynamicCaptions,
      hashtags: data.hashtags?.length > 0 ? data.hashtags : dynamicHashtags,
      metadata: {
        prompt: enhancedPrompt,
        generated_at: new Date().toISOString(),
        ai_service: 'backend',
        unique_id: data.metadata?.unique_id || `gen_${Date.now()}`
      }
    }

