// Fix for the URL validation issue in enhanced-poster-generator.tsx
// Replace the URL validation section (around lines 278-287) with this:

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function urlValidationSnippet() {
    // Type declarations for snippet context
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data: any = {} as any
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const setGenerationError: any = () => {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const setAiServiceStatus: any = () => {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const showError: any = () => {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const dynamicCaptions: any = []
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const dynamicHashtags: any = []
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const enhancedPrompt: any = ''

    // Handle both relative and absolute URLs
    let finalImageUrl = data.poster_url

    // If it's a relative URL, make it absolute
    if (data.poster_url.startsWith('/')) {
      // Import getFullUrl from @/utils/api in the actual component
      // const { getFullUrl } = require('@/utils/api')
      // finalImageUrl = getFullUrl(data.poster_url)
      // For this snippet, use API_BASE_URL pattern:
      const { API_BASE_URL } = require('@/utils/api')
      finalImageUrl = `${API_BASE_URL}${data.poster_url}`
      console.log('🔗 Converted relative URL to absolute:', finalImageUrl)
    }

    // Validate the final URL
    try {
      new URL(finalImageUrl)
    } catch {
      console.error('❌ Invalid poster URL format:', finalImageUrl)
      setGenerationError('Invalid image URL generated. Please try again.')
      setAiServiceStatus('error')
      showError('Invalid image URL generated. Please try again.')
      return
    }

// And then update the posterData to use finalImageUrl instead of data.poster_url:

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const _posterData = {
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
}










