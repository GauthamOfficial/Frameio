import { Page, APIRequestContext } from '@playwright/test';

export interface TestOrganization {
  id: string;
  name: string;
  slug: string;
  subscription_plan: string;
}

export interface TestUser {
  id: string;
  username: string;
  email: string;
  clerk_id: string;
}

export interface TestAIProvider {
  id: string;
  name: string;
  is_active: boolean;
  rate_limit_per_minute: number;
  rate_limit_per_hour: number;
}

export interface TestGenerationRequest {
  id: string;
  provider: string;
  generation_type: string;
  prompt: string;
  status: string;
  result_urls?: string[];
  created_at: string;
  completed_at?: string;
}

export interface TestTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  prompt_template: string;
  default_parameters: Record<string, any>;
  usage_count: number;
  is_public: boolean;
}

export class AITestHelper {
  constructor(private page: Page, private request: APIRequestContext) {}

  /**
   * Setup mock responses for AI services API
   */
  async setupMockResponses() {
    await this.page.route('**/api/ai/**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      
      // Handle different endpoints
      if (url.includes('/providers/') && method === 'GET') {
        await this.mockProvidersResponse(route);
      } else if (url.includes('/generation-requests/') && method === 'POST') {
        await this.mockCreateGenerationRequest(route);
      } else if (url.includes('/generation-requests/') && method === 'GET') {
        await this.mockListGenerationRequests(route);
      } else if (url.includes('/templates/') && method === 'GET') {
        await this.mockListTemplates(route);
      } else if (url.includes('/quotas/') && method === 'GET') {
        await this.mockListQuotas(route);
      } else if (url.includes('/analytics/dashboard/') && method === 'GET') {
        await this.mockAnalyticsDashboard(route);
      } else {
        await route.continue();
      }
    });
  }

  /**
   * Mock AI providers response
   */
  private async mockProvidersResponse(route: any) {
    const providers: TestAIProvider[] = [
      {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'nanobanana',
        is_active: true,
        rate_limit_per_minute: 60,
        rate_limit_per_hour: 1000
      },
      {
        id: '234e5678-e89b-12d3-a456-426614174001',
        name: 'openai',
        is_active: true,
        rate_limit_per_minute: 30,
        rate_limit_per_hour: 500
      }
    ];

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        count: providers.length,
        results: providers
      })
    });
  }

  /**
   * Mock create generation request
   */
  private async mockCreateGenerationRequest(route: any) {
    const requestData = route.request().postDataJSON();
    
    // Validate request
    if (!requestData?.prompt || requestData.prompt.trim() === '') {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          prompt: ['Prompt cannot be empty']
        })
      });
      return;
    }

    // Check for suspicious content
    if (requestData.prompt.toLowerCase().includes('jailbreak')) {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Request contains potentially harmful content',
          code: 'CONTENT_POLICY_VIOLATION'
        })
      });
      return;
    }

    const generationRequest: TestGenerationRequest = {
      id: `gen-${Date.now()}`,
      provider: requestData.provider,
      generation_type: requestData.generation_type,
      prompt: requestData.prompt,
      status: 'pending',
      created_at: new Date().toISOString()
    };

    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify(generationRequest)
    });
  }

  /**
   * Mock list generation requests
   */
  private async mockListGenerationRequests(route: any) {
    const url = new URL(route.request().url());
    const generationType = url.searchParams.get('generation_type');
    const status = url.searchParams.get('status');

    let requests: TestGenerationRequest[] = [
      {
        id: 'gen-1',
        provider: '123e4567-e89b-12d3-a456-426614174000',
        generation_type: 'poster',
        prompt: 'Create a beautiful textile design',
        status: 'completed',
        result_urls: ['https://example.com/image1.png'],
        created_at: '2024-01-01T00:00:00Z',
        completed_at: '2024-01-01T00:00:30Z'
      },
      {
        id: 'gen-2',
        provider: '123e4567-e89b-12d3-a456-426614174000',
        generation_type: 'catalog',
        prompt: 'Create a product catalog layout',
        status: 'processing',
        created_at: '2024-01-01T01:00:00Z'
      }
    ];

    // Apply filters
    if (generationType) {
      requests = requests.filter(r => r.generation_type === generationType);
    }
    if (status) {
      requests = requests.filter(r => r.status === status);
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        count: requests.length,
        results: requests
      })
    });
  }

  /**
   * Mock list templates
   */
  private async mockListTemplates(route: any) {
    const url = new URL(route.request().url());
    const category = url.searchParams.get('category');

    let templates: TestTemplate[] = [
      {
        id: 'template-1',
        name: 'Floral Design Template',
        category: 'textile',
        description: 'Beautiful floral patterns for textiles',
        prompt_template: 'Create a {style} floral design with {colors}',
        default_parameters: { width: 1024, height: 1024 },
        usage_count: 15,
        is_public: false
      },
      {
        id: 'template-2',
        name: 'Modern Geometric Template',
        category: 'poster',
        description: 'Clean geometric patterns',
        prompt_template: 'Create a {style} geometric design',
        default_parameters: { width: 800, height: 600 },
        usage_count: 8,
        is_public: true
      }
    ];

    // Apply category filter
    if (category) {
      templates = templates.filter(t => t.category === category);
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        count: templates.length,
        results: templates
      })
    });
  }

  /**
   * Mock list quotas
   */
  private async mockListQuotas(route: any) {
    const quotas = [
      {
        id: 'quota-1',
        provider_name: 'NanoBanana',
        generation_type: 'poster',
        quota_type: 'monthly',
        max_requests: 1000,
        current_requests: 150,
        max_cost: 100.00,
        current_cost: 15.50,
        usage_percentage: 15.0,
        cost_percentage: 15.5,
        reset_at: '2024-02-01T00:00:00Z'
      }
    ];

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        count: quotas.length,
        results: quotas
      })
    });
  }

  /**
   * Mock analytics dashboard
   */
  private async mockAnalyticsDashboard(route: any) {
    const analytics = {
      total_requests: 150,
      successful_requests: 142,
      failed_requests: 8,
      success_rate: 94.67,
      average_processing_time: 12.5,
      total_cost: 15.50,
      most_used_generation_type: 'poster',
      most_used_provider: 'nanobanana',
      quota_usage_by_type: {
        'poster_monthly': {
          current_requests: 150,
          max_requests: 1000,
          usage_percentage: 15.0
        }
      }
    };

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(analytics)
    });
  }

  /**
   * Mock rate limiting response
   */
  async mockRateLimitResponse() {
    await this.page.route('**/api/ai/generation-requests/', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 429,
          contentType: 'application/json',
          body: JSON.stringify({
            error: 'Rate limit exceeded for ai_generation',
            limit: 10,
            window_seconds: 60,
            retry_after: 45
          })
        });
      }
    });
  }

  /**
   * Mock high quota usage
   */
  async mockHighQuotaUsage() {
    await this.page.route('**/api/ai/quotas/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          results: [{
            id: 'quota-1',
            provider_name: 'NanoBanana',
            generation_type: 'poster',
            quota_type: 'monthly',
            max_requests: 1000,
            current_requests: 950,
            usage_percentage: 95.0,
            reset_at: '2024-02-01T00:00:00Z'
          }]
        })
      });
    });
  }

  /**
   * Create test organization via API
   */
  async createTestOrganization(): Promise<TestOrganization> {
    const response = await this.request.post('/api/organizations/', {
      data: {
        name: 'AI Test Organization',
        slug: 'ai-test-org',
        subscription_plan: 'pro'
      }
    });

    if (!response.ok()) {
      throw new Error(`Failed to create test organization: ${response.status()}`);
    }

    return await response.json();
  }

  /**
   * Create test user via API
   */
  async createTestUser(): Promise<TestUser> {
    const response = await this.request.post('/api/users/', {
      data: {
        username: 'aitestuser',
        email: 'ai-test@example.com',
        clerk_id: 'test_clerk_123'
      }
    });

    if (!response.ok()) {
      throw new Error(`Failed to create test user: ${response.status()}`);
    }

    return await response.json();
  }

  /**
   * Navigate to AI services section
   */
  async navigateToAIServices() {
    await this.page.goto('/dashboard/ai-services');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Fill generation form
   */
  async fillGenerationForm(data: {
    provider?: string;
    generationType?: string;
    prompt: string;
    parameters?: Record<string, any>;
  }) {
    if (data.provider) {
      await this.page.selectOption('[data-testid="provider-select"]', data.provider);
    }
    
    if (data.generationType) {
      await this.page.selectOption('[data-testid="generation-type-select"]', data.generationType);
    }
    
    await this.page.fill('[data-testid="prompt-input"]', data.prompt);
    
    if (data.parameters) {
      // Fill parameter fields if they exist
      for (const [key, value] of Object.entries(data.parameters)) {
        const field = this.page.locator(`[data-testid="param-${key}"]`);
        if (await field.isVisible()) {
          await field.fill(String(value));
        }
      }
    }
  }

  /**
   * Submit generation form
   */
  async submitGenerationForm() {
    await this.page.click('[data-testid="generate-button"]');
  }

  /**
   * Wait for generation to complete
   */
  async waitForGenerationComplete(requestId: string, timeout = 30000) {
    await this.page.waitForFunction(
      (id) => {
        const statusElement = document.querySelector(`[data-testid="status-${id}"]`);
        return statusElement?.textContent?.toLowerCase().includes('completed');
      },
      requestId,
      { timeout }
    );
  }

  /**
   * Check if element contains error message
   */
  async expectErrorMessage(selector: string, message: string) {
    const element = this.page.locator(selector);
    await element.waitFor();
    const text = await element.textContent();
    if (!text?.includes(message)) {
      throw new Error(`Expected error message "${message}" not found in "${text}"`);
    }
  }

  /**
   * Check if quota warning is displayed
   */
  async expectQuotaWarning() {
    await this.page.locator('[data-testid="quota-warning"]').waitFor();
  }

  /**
   * Get analytics data from dashboard
   */
  async getAnalyticsData() {
    await this.page.goto('/dashboard/ai-services/analytics');
    await this.page.waitForLoadState('networkidle');
    
    const totalRequests = await this.page.textContent('[data-testid="total-requests"]');
    const successRate = await this.page.textContent('[data-testid="success-rate"]');
    const totalCost = await this.page.textContent('[data-testid="total-cost"]');
    
    return {
      totalRequests: totalRequests ? parseInt(totalRequests) : 0,
      successRate: successRate ? parseFloat(successRate) : 0,
      totalCost: totalCost ? parseFloat(totalCost.replace('$', '')) : 0
    };
  }
}
