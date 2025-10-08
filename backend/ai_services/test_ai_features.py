"""
Comprehensive Tests for Phase 1 Week 4 AI Features
Tests for color matching, fabric analysis, background generation, and usage tracking
"""
import pytest
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from .models import AIGenerationRequest, AIProvider, AIUsageQuota
from .color_matching import SmartColorMatcher
from .fabric_analysis import FabricAnalyzer
from .background_generator import AIBackgroundGenerator
from .usage_tracker import UsageTracker, BillingManager
from organizations.models import Organization

User = get_user_model()


class SmartColorMatcherTests(TestCase):
    """Tests for Smart Color Matching algorithms"""
    
    def setUp(self):
        self.color_matcher = SmartColorMatcher()
        self.sample_fabric_colors = [
            {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'lab': [65, 45, 25], 'percentage': 35},
            {'hex': '#4ECDC4', 'rgb': [78, 205, 196], 'lab': [75, -25, -5], 'percentage': 25},
            {'hex': '#45B7D1', 'rgb': [69, 183, 209], 'lab': [70, -15, -20], 'percentage': 20}
        ]
        self.sample_design_colors = [
            {'hex': '#FF9F43', 'rgb': [255, 159, 67], 'lab': [75, 35, 50], 'percentage': 30},
            {'hex': '#6C5CE7', 'rgb': [108, 92, 231], 'lab': [50, 25, -45], 'percentage': 25},
            {'hex': '#A29BFE', 'rgb': [162, 155, 254], 'lab': [70, 15, -35], 'percentage': 20}
        ]
    
    def test_extract_dominant_colors_mock(self):
        """Test color extraction with mock image"""
        with patch.object(self.color_matcher, '_download_image') as mock_download:
            # Mock image data
            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_download.return_value = mock_image
            
            colors = self.color_matcher.extract_dominant_colors("http://example.com/image.jpg", 5)
            
            self.assertIsInstance(colors, list)
            self.assertLessEqual(len(colors), 5)
            
            if colors:
                color = colors[0]
                self.assertIn('hex', color)
                self.assertIn('rgb', color)
                self.assertIn('lab', color)
                self.assertIn('percentage', color)
    
    def test_match_colors(self):
        """Test color matching between fabric and design"""
        result = self.color_matcher.match_colors(self.sample_fabric_colors, self.sample_design_colors)
        
        self.assertIn('matches', result)
        self.assertIn('unmatched_fabric', result)
        self.assertIn('unmatched_design', result)
        self.assertIn('overall_matching_score', result)
        self.assertIn('harmony_suggestions', result)
        
        self.assertIsInstance(result['matches'], list)
        self.assertIsInstance(result['overall_matching_score'], (int, float))
    
    def test_suggest_color_adjustments(self):
        """Test color adjustment suggestions"""
        suggestions = self.color_matcher.suggest_color_adjustments(
            self.sample_fabric_colors, 'complementary'
        )
        
        self.assertIsInstance(suggestions, list)
        
        if suggestions:
            suggestion = suggestions[0]
            self.assertIn('original_color', suggestion)
            self.assertIn('target_harmony', suggestion)
            self.assertIn('suggested_colors', suggestion)
            self.assertIn('confidence', suggestion)
    
    def test_calculate_lab_distance(self):
        """Test LAB color distance calculation"""
        lab1 = [65, 45, 25]
        lab2 = [70, 40, 30]
        
        distance = self.color_matcher._calculate_lab_distance(lab1, lab2)
        
        self.assertIsInstance(distance, (int, float))
        self.assertGreaterEqual(distance, 0)
    
    def test_get_complementary_colors(self):
        """Test complementary color generation"""
        base_color = self.sample_fabric_colors[0]
        complementary = self.color_matcher._get_complementary_colors(base_color)
        
        self.assertIsInstance(complementary, list)
        self.assertGreater(len(complementary), 0)
        
        if complementary:
            comp_color = complementary[0]
            self.assertIn('hex', comp_color)
            self.assertIn('rgb', comp_color)
            self.assertIn('relationship', comp_color)


class FabricAnalyzerTests(TestCase):
    """Tests for Fabric Analysis service"""
    
    def setUp(self):
        self.fabric_analyzer = FabricAnalyzer()
        self.sample_image_url = "http://example.com/fabric.jpg"
    
    @patch('requests.get')
    def test_analyze_fabric_mock(self, mock_get):
        """Test fabric analysis with mock image"""
        # Mock image response
        mock_response = Mock()
        mock_response.content = b'fake_image_data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('PIL.Image.open') as mock_image_open:
            mock_image = Mock()
            mock_image_open.return_value = mock_image
            
            result = self.fabric_analyzer.analyze_fabric(self.sample_image_url, 'comprehensive')
            
            self.assertIn('success', result)
            self.assertIn('image_url', result)
            self.assertIn('analysis_type', result)
            
            if result['success']:
                self.assertIn('color_analysis', result)
                self.assertIn('texture_analysis', result)
                self.assertIn('pattern_analysis', result)
                self.assertIn('quality_assessment', result)
                self.assertIn('recommendations', result)
    
    def test_extract_color_palette_mock(self):
        """Test color palette extraction"""
        with patch.object(self.fabric_analyzer.color_matcher, 'extract_dominant_colors') as mock_extract:
            mock_extract.return_value = [
                {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'lab': [65, 45, 25], 'percentage': 35},
                {'hex': '#4ECDC4', 'rgb': [78, 205, 196], 'lab': [75, -25, -5], 'percentage': 25}
            ]
            
            result = self.fabric_analyzer.extract_color_palette(self.sample_image_url, 5)
            
            self.assertIn('success', result)
            self.assertIn('color_palette', result)
            self.assertIn('harmony_analysis', result)
            
            if result['success']:
                self.assertIsInstance(result['color_palette'], list)
                self.assertIn('total_colors', result)
                self.assertIn('dominant_color', result)
    
    def test_analyze_texture_patterns_mock(self):
        """Test texture pattern analysis"""
        with patch.object(self.fabric_analyzer, '_download_image') as mock_download:
            mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_download.return_value = mock_image
            
            result = self.fabric_analyzer.analyze_texture_patterns(self.sample_image_url)
            
            self.assertIn('success', result)
            self.assertIn('texture_features', result)
            self.assertIn('pattern_features', result)
            self.assertIn('fabric_type', result)
            
            if result['success']:
                self.assertIn('texture_quality', result)
                self.assertIn('pattern_complexity', result)
    
    def test_get_color_family(self):
        """Test color family classification"""
        color = {'hsv': [0, 100, 100]}  # Red
        family = self.fabric_analyzer._get_color_family(color)
        
        self.assertEqual(family, 'Red')
    
    def test_get_seasonal_association(self):
        """Test seasonal color association"""
        color = {'hsv': [120, 100, 100]}  # Green
        season = self.fabric_analyzer._get_seasonal_association(color)
        
        self.assertIn(season, ['Spring', 'Summer', 'Autumn', 'Winter', 'All Seasons'])


class AIBackgroundGeneratorTests(TestCase):
    """Tests for AI Background Generator"""
    
    def setUp(self):
        self.background_generator = AIBackgroundGenerator()
        self.sample_fabric_url = "http://example.com/fabric.jpg"
        self.mock_organization = Mock()
        self.mock_user = Mock()
    
    def test_create_fabric_background_prompt(self):
        """Test fabric background prompt creation"""
        fabric_analysis = {
            'dominant_colors': [
                {'hex': '#FF6B6B', 'name': 'Red'},
                {'hex': '#4ECDC4', 'name': 'Teal'}
            ],
            'fabric_mood': 'elegant',
            'color_temperature': 'warm',
            'texture_type': 'smooth',
            'pattern_type': 'geometric'
        }
        
        prompt = self.background_generator._create_fabric_background_prompt(
            fabric_analysis, 'complementary', 'seamless', 'medium'
        )
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn('seamless', prompt.lower())
        self.assertIn('complementary', prompt.lower())
    
    def test_create_texture_background_prompt(self):
        """Test texture background prompt creation"""
        prompt = self.background_generator._create_texture_background_prompt(
            "organic flowing texture", ['#FF6B6B', '#4ECDC4'], 'organic'
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn('organic flowing texture', prompt)
        self.assertIn('#FF6B6B', prompt)
        self.assertIn('organic', prompt.lower())
    
    def test_create_seamless_pattern_prompt(self):
        """Test seamless pattern prompt creation"""
        color_palette = [
            {'hex': '#FF6B6B', 'name': 'Red'},
            {'hex': '#4ECDC4', 'name': 'Teal'}
        ]
        
        prompt = self.background_generator._create_seamless_pattern_prompt(
            "geometric pattern", color_palette
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn('geometric pattern', prompt)
        self.assertIn('seamless', prompt.lower())
        self.assertIn('#FF6B6B', prompt)
    
    def test_get_background_presets(self):
        """Test background presets"""
        presets = self.background_generator.get_background_presets()
        
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        
        for preset in presets:
            self.assertIn('id', preset)
            self.assertIn('name', preset)
            self.assertIn('description', preset)
            self.assertIn('best_for', preset)
    
    def test_calculate_compatibility_score(self):
        """Test compatibility score calculation"""
        variation = {
            'parameters': {'guidance_scale': 7.5, 'steps': 20},
            'cost': 0.05,
            'processing_time': 15
        }
        
        fabric_analysis = {
            'fabric_mood': 'elegant',
            'color_temperature': 'warm',
            'pattern_complexity': 'medium'
        }
        
        score = self.background_generator._calculate_compatibility_score(
            variation, fabric_analysis, 'complementary'
        )
        
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)


class UsageTrackerTests(TestCase):
    """Tests for Usage Tracking and Billing"""
    
    def setUp(self):
        self.usage_tracker = UsageTracker()
        self.mock_organization = Mock()
        self.mock_user = Mock()
        self.mock_organization.name = "Test Organization"
        self.mock_user.email = "test@example.com"
    
    def test_track_usage_mock(self):
        """Test usage tracking with mock data"""
        with patch.object(self.usage_tracker, '_update_quota') as mock_update:
            mock_update.return_value = {
                'quota_exceeded': False,
                'current_requests': 5,
                'max_requests': 100,
                'current_cost': 10.0,
                'max_cost': 100.0
            }
            
            result = self.usage_tracker.track_usage(
                self.mock_organization,
                self.mock_user,
                'fabric_analysis',
                0.05,
                'nanobanana'
            )
            
            self.assertIn('success', result)
            self.assertIn('quota_exceeded', result)
            self.assertIn('monthly_quota', result)
            self.assertIn('daily_quota', result)
            self.assertIn('hourly_quota', result)
    
    def test_check_quota_mock(self):
        """Test quota checking with mock data"""
        with patch('ai_services.models.AIUsageQuota.objects.filter') as mock_filter:
            mock_quota = Mock()
            mock_quota.current_requests = 10
            mock_quota.max_requests = 100
            mock_quota.current_cost = 5.0
            mock_quota.max_cost = 50.0
            mock_quota.is_quota_exceeded.return_value = False
            mock_quota.reset_at = timezone.now()
            
            mock_filter.return_value.first.return_value = mock_quota
            
            result = self.usage_tracker.check_quota(
                self.mock_organization,
                'fabric_analysis',
                'nanobanana'
            )
            
            self.assertIn('success', result)
            self.assertIn('quota_exceeded', result)
            self.assertIn('quotas', result)
    
    def test_get_usage_analytics_mock(self):
        """Test usage analytics with mock data"""
        with patch('ai_services.models.AIGenerationRequest.objects.filter') as mock_filter:
            mock_requests = Mock()
            mock_requests.count.return_value = 50
            mock_requests.filter.return_value.count.return_value = 45
            mock_requests.aggregate.return_value = {'total': 25.0, 'avg': 0.5}
            mock_requests.values.return_value.distinct.return_value = [{'provider__name': 'nanobanana'}]
            mock_requests.values_list.return_value = [10, 15, 20, 25, 30]
            
            mock_filter.return_value = mock_requests
            
            result = self.usage_tracker.get_usage_analytics(self.mock_organization, 30)
            
            self.assertIn('success', result)
            self.assertIn('summary', result)
            self.assertIn('usage_by_type', result)
            self.assertIn('usage_by_provider', result)
            self.assertIn('daily_trends', result)
    
    @patch('stripe.Customer.create')
    def test_create_billing_invoice_mock(self, mock_stripe_create):
        """Test billing invoice creation with mock Stripe"""
        mock_customer = Mock()
        mock_customer.id = 'cus_test123'
        mock_stripe_create.return_value = mock_customer
        
        with patch('stripe.InvoiceItem.create') as mock_invoice_item, \
             patch('stripe.Invoice.create') as mock_invoice_create:
            
            mock_invoice = Mock()
            mock_invoice.id = 'in_test123'
            mock_invoice.status = 'paid'
            mock_invoice.paid = True
            mock_invoice_create.return_value = mock_invoice
            
            result = self.usage_tracker.create_billing_invoice(
                self.mock_organization,
                25.0,
                "Test invoice"
            )
            
            self.assertIn('success', result)
            self.assertIn('invoice_id', result)
            self.assertIn('amount', result)


class BillingManagerTests(TestCase):
    """Tests for Billing Manager"""
    
    def setUp(self):
        self.billing_manager = BillingManager()
        self.mock_organization = Mock()
        self.mock_organization.name = "Test Organization"
        self.mock_organization.id = 1
    
    @patch('stripe.Customer.create')
    def test_setup_organization_billing_mock(self, mock_stripe_create):
        """Test organization billing setup with mock Stripe"""
        mock_customer = Mock()
        mock_customer.id = 'cus_test123'
        mock_stripe_create.return_value = mock_customer
        
        billing_info = {
            'email': 'billing@test.com',
            'phone': '+1234567890',
            'address_line1': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'postal_code': '12345',
            'country': 'US'
        }
        
        result = self.billing_manager.setup_organization_billing(
            self.mock_organization,
            billing_info
        )
        
        self.assertIn('success', result)
        self.assertIn('customer_id', result)
    
    def test_get_billing_summary_mock(self):
        """Test billing summary with mock data"""
        with patch.object(self.billing_manager.usage_tracker, 'get_usage_analytics') as mock_analytics, \
             patch.object(self.billing_manager.usage_tracker, '_get_quota_status') as mock_quota:
            
            mock_analytics.return_value = {
                'success': True,
                'summary': {
                    'total_cost': 50.0,
                    'total_requests': 100
                }
            }
            
            mock_quota.return_value = {
                'nanobanana_fabric_analysis': {
                    'current_requests': 10,
                    'max_requests': 100,
                    'quota_exceeded': False
                }
            }
            
            result = self.billing_manager.get_billing_summary(self.mock_organization)
            
            self.assertIn('success', result)
            self.assertIn('current_month', result)
            self.assertIn('quota_status', result)


class FabricAnalysisAPITests(APITestCase):
    """API Tests for Fabric Analysis endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            description='Test organization for API tests'
        )
        self.client.force_login(self.user)
    
    @patch('ai_services.fabric_analysis.FabricAnalyzer.analyze_fabric')
    def test_analyze_fabric_endpoint(self, mock_analyze):
        """Test fabric analysis API endpoint"""
        mock_analyze.return_value = {
            'success': True,
            'image_url': 'http://example.com/fabric.jpg',
            'color_analysis': {
                'dominant_colors': [
                    {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'percentage': 35}
                ]
            },
            'texture_analysis': {
                'texture_type': 'smooth',
                'fabric_type': {'predicted_type': 'cotton'}
            }
        }
        
        url = reverse('fabric-analysis-analyze-fabric')
        data = {
            'fabric_image_url': 'http://example.com/fabric.jpg',
            'analysis_type': 'comprehensive'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    @patch('ai_services.fabric_analysis.FabricAnalyzer.extract_color_palette')
    def test_extract_colors_endpoint(self, mock_extract):
        """Test color extraction API endpoint"""
        mock_extract.return_value = {
            'success': True,
            'color_palette': [
                {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'lab': [65, 45, 25], 'percentage': 35}
            ],
            'total_colors': 1
        }
        
        url = reverse('fabric-analysis-extract-colors')
        data = {
            'fabric_image_url': 'http://example.com/fabric.jpg',
            'num_colors': 5
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    @patch('ai_services.color_matching.SmartColorMatcher.match_colors')
    def test_match_colors_endpoint(self, mock_match):
        """Test color matching API endpoint"""
        mock_match.return_value = {
            'matches': [
                {
                    'fabric_color': {'hex': '#FF6B6B'},
                    'design_color': {'hex': '#FF9F43'},
                    'distance': 15.5,
                    'similarity_score': 85.5
                }
            ],
            'overall_matching_score': 85.5
        }
        
        url = reverse('fabric-analysis-match-colors')
        data = {
            'fabric_colors': [
                {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'lab': [65, 45, 25], 'percentage': 35}
            ],
            'design_colors': [
                {'hex': '#FF9F43', 'rgb': [255, 159, 67], 'lab': [75, 35, 50], 'percentage': 30}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    def test_analysis_history_endpoint(self):
        """Test analysis history API endpoint"""
        url = reverse('fabric-analysis-analysis-history')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('history', response.data)


class IntegrationTests(TestCase):
    """Integration tests for AI features"""
    
    def setUp(self):
        self.color_matcher = SmartColorMatcher()
        self.fabric_analyzer = FabricAnalyzer()
        self.background_generator = AIBackgroundGenerator()
        self.usage_tracker = UsageTracker()
    
    def test_end_to_end_fabric_analysis_workflow(self):
        """Test complete fabric analysis workflow"""
        # Mock the entire workflow
        with patch.object(self.fabric_analyzer, 'analyze_fabric') as mock_analyze:
            mock_analyze.return_value = {
                'success': True,
                'color_analysis': {
                    'dominant_colors': [
                        {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'lab': [65, 45, 25], 'percentage': 35}
                    ]
                }
            }
            
            # Step 1: Analyze fabric
            fabric_analysis = self.fabric_analyzer.analyze_fabric("http://example.com/fabric.jpg")
            
            self.assertTrue(fabric_analysis['success'])
            
            # Step 2: Extract colors for matching
            fabric_colors = fabric_analysis['color_analysis']['dominant_colors']
            design_colors = [
                {'hex': '#FF9F43', 'rgb': [255, 159, 67], 'lab': [75, 35, 50], 'percentage': 30}
            ]
            
            # Step 3: Match colors
            match_result = self.color_matcher.match_colors(fabric_colors, design_colors)
            
            self.assertIn('matches', match_result)
            self.assertIn('overall_matching_score', match_result)
            
            # Step 4: Generate background (mock)
            with patch.object(self.background_generator, '_analyze_fabric_for_background') as mock_bg_analyze:
                mock_bg_analyze.return_value = fabric_analysis
                
                background_result = self.background_generator.generate_fabric_background(
                    Mock(), Mock(), "http://example.com/fabric.jpg"
                )
                
                self.assertIn('success', background_result)
    
    def test_usage_tracking_integration(self):
        """Test usage tracking integration"""
        mock_organization = Mock()
        mock_user = Mock()
        
        with patch.object(self.usage_tracker, '_update_quota') as mock_update:
            mock_update.return_value = {
                'quota_exceeded': False,
                'current_requests': 1,
                'max_requests': 100
            }
            
            # Track usage
            result = self.usage_tracker.track_usage(
                mock_organization,
                mock_user,
                'fabric_analysis',
                0.05
            )
            
            self.assertTrue(result['success'])
            self.assertFalse(result['quota_exceeded'])


if __name__ == '__main__':
    pytest.main([__file__])

