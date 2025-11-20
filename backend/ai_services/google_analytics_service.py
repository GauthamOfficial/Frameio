"""
Google Analytics Data API (GA4) Service
Fetches real analytics data from Google Analytics 4
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
try:
    from google.analytics.data import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        DateRange,
        Dimension,
        Metric,
        OrderBy,
    )
except ImportError:
    # Fallback if library is not installed
    BetaAnalyticsDataClient = None
    RunReportRequest = None
    DateRange = None
    Dimension = None
    Metric = None
    OrderBy = None

try:
    from google.oauth2 import service_account
except ImportError:
    service_account = None

import json

logger = logging.getLogger(__name__)


class GoogleAnalyticsService:
    """Service for fetching data from Google Analytics Data API (GA4)"""
    
    def __init__(self):
        """Initialize the Google Analytics service"""
        if BetaAnalyticsDataClient is None:
            logger.warning("Google Analytics Data API library not installed. Run: pip install google-analytics-data")
            self.client = None
            self.property_id = None
            return
            
        self.property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
        self.credentials_path = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_PATH')
        self.credentials_json = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_JSON')
        
        if not self.property_id:
            logger.warning("GOOGLE_ANALYTICS_PROPERTY_ID not set. Analytics will not work.")
            self.client = None
            return
        
        try:
            if service_account is None:
                logger.warning("google-auth library not installed. Run: pip install google-auth")
                self.client = None
                return
                
            # Initialize credentials
            credentials = None
            if self.credentials_json:
                # Use JSON string from environment variable
                # Remove surrounding quotes if present (from .env file)
                creds_json = self.credentials_json.strip()
                if creds_json.startswith("'") and creds_json.endswith("'"):
                    creds_json = creds_json[1:-1]
                elif creds_json.startswith('"') and creds_json.endswith('"'):
                    creds_json = creds_json[1:-1]
                
                try:
                    credentials_info = json.loads(creds_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=['https://www.googleapis.com/auth/analytics.readonly']
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GOOGLE_ANALYTICS_CREDENTIALS_JSON: {str(e)}")
                    self.client = None
                    return
            elif self.credentials_path and os.path.exists(self.credentials_path):
                # Use credentials file path
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
            else:
                logger.warning("Google Analytics credentials not configured. Set GOOGLE_ANALYTICS_CREDENTIALS_JSON or GOOGLE_ANALYTICS_CREDENTIALS_PATH")
                self.client = None
                return
            
            # Initialize the client
            self.client = BetaAnalyticsDataClient(credentials=credentials)
            logger.info("Google Analytics service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics service: {str(e)}")
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self.client is not None and self.property_id is not None
    
    def _get_date_range(self, days: int = 30) -> tuple:
        """Get start and end dates for the date range"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def _get_previous_date_range(self, days: int = 30) -> tuple:
        """Get previous period date range for comparison"""
        end_date = datetime.now().date() - timedelta(days=days)
        start_date = end_date - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def get_overview_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get overview statistics including:
        - Total users
        - Total sessions
        - Page views
        - Average session duration
        - Bounce rate
        """
        if not self.is_configured():
            return {
                'error': 'Google Analytics not configured',
                'totalUsers': 0,
                'totalSessions': 0,
                'pageViews': 0,
                'avgSessionDuration': '0s',
                'bounceRate': '0%'
            }
        
        try:
            start_date, end_date = self._get_date_range(days)
            prev_start, prev_end = self._get_previous_date_range(days)
            
            # Current period metrics
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate"),
                ],
            )
            
            response = self.client.run_report(request)
            
            # Previous period for comparison
            prev_request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=prev_start, end_date=prev_end)],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                ],
            )
            
            prev_response = self.client.run_report(prev_request)
            
            # Extract current period data
            current_row = response.rows[0] if response.rows else None
            prev_row = prev_response.rows[0] if prev_response.rows else None
            
            if not current_row:
                return {
                    'error': 'No data available',
                    'totalUsers': 0,
                    'totalSessions': 0,
                    'pageViews': 0,
                    'avgSessionDuration': '0s',
                    'bounceRate': '0%'
                }
            
            # Parse metrics
            total_users = int(current_row.metric_values[0].value)
            total_sessions = int(current_row.metric_values[1].value)
            page_views = int(current_row.metric_values[2].value)
            avg_duration_seconds = float(current_row.metric_values[3].value)
            bounce_rate = float(current_row.metric_values[4].value) * 100
            
            # Format duration
            minutes = int(avg_duration_seconds // 60)
            seconds = int(avg_duration_seconds % 60)
            avg_duration = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            
            # Calculate trends
            prev_users = int(prev_row.metric_values[0].value) if prev_row else total_users
            prev_sessions = int(prev_row.metric_values[1].value) if prev_row else total_sessions
            prev_views = int(prev_row.metric_values[2].value) if prev_row else page_views
            
            user_trend = ((total_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
            session_trend = ((total_sessions - prev_sessions) / prev_sessions * 100) if prev_sessions > 0 else 0
            views_trend = ((page_views - prev_views) / prev_views * 100) if prev_views > 0 else 0
            
            return {
                'totalUsers': total_users,
                'totalSessions': total_sessions,
                'pageViews': page_views,
                'avgSessionDuration': avg_duration,
                'bounceRate': f"{bounce_rate:.1f}%",
                'trends': {
                    'users': f"{user_trend:+.1f}%",
                    'sessions': f"{session_trend:+.1f}%",
                    'views': f"{views_trend:+.1f}%",
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching overview stats: {str(e)}")
            return {
                'error': str(e),
                'totalUsers': 0,
                'totalSessions': 0,
                'pageViews': 0,
                'avgSessionDuration': '0s',
                'bounceRate': '0%'
            }
    
    def get_user_growth_data(self, days: int = 180) -> List[Dict[str, Any]]:
        """Get user growth data over time"""
        if not self.is_configured():
            return []
        
        try:
            start_date, end_date = self._get_date_range(days)
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="yearMonth")],
                metrics=[Metric(name="activeUsers")],
                order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="yearMonth"))],
            )
            
            response = self.client.run_report(request)
            
            data = []
            for row in response.rows:
                year_month = row.dimension_values[0].value
                # Format: YYYYMM -> "Jan 2024"
                year = year_month[:4]
                month_num = int(year_month[4:])
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                label = f"{month_names[month_num - 1]} {year}"
                value = int(row.metric_values[0].value)
                data.append({'label': label, 'value': value})
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching user growth data: {str(e)}")
            return []
    
    def get_device_breakdown(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get device breakdown (Desktop, Mobile, Tablet)"""
        if not self.is_configured():
            return []
        
        try:
            start_date, end_date = self._get_date_range(days)
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="deviceCategory")],
                metrics=[Metric(name="sessions")],
            )
            
            response = self.client.run_report(request)
            
            total_sessions = 0
            device_data = {}
            
            for row in response.rows:
                device = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                device_data[device] = sessions
                total_sessions += sessions
            
            # Convert to percentages
            data = []
            device_mapping = {
                'desktop': 'Desktop',
                'mobile': 'Mobile',
                'tablet': 'Tablet'
            }
            
            for device, sessions in device_data.items():
                percentage = (sessions / total_sessions * 100) if total_sessions > 0 else 0
                label = device_mapping.get(device.lower(), device.capitalize())
                data.append({'label': label, 'value': round(percentage, 1)})
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching device breakdown: {str(e)}")
            return []
    
    def get_top_pages(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top pages by page views"""
        if not self.is_configured():
            return []
        
        try:
            start_date, end_date = self._get_date_range(days)
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="pagePath")],
                metrics=[Metric(name="screenPageViews")],
                order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
                limit=limit,
            )
            
            response = self.client.run_report(request)
            
            data = []
            for row in response.rows:
                page_path = row.dimension_values[0].value
                views = int(row.metric_values[0].value)
                data.append({
                    'path': page_path,
                    'views': views,
                    'title': page_path.split('/')[-1] or 'Home'
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching top pages: {str(e)}")
            return []
    
    def get_traffic_sources(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get traffic sources breakdown"""
        if not self.is_configured():
            return []
        
        try:
            start_date, end_date = self._get_date_range(days)
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="sessionSource")],
                metrics=[Metric(name="sessions")],
                order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
                limit=10,
            )
            
            response = self.client.run_report(request)
            
            data = []
            for row in response.rows:
                source = row.dimension_values[0].value or 'direct'
                sessions = int(row.metric_values[0].value)
                data.append({
                    'source': source,
                    'sessions': sessions
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching traffic sources: {str(e)}")
            return []


# Singleton instance
_ga_service = None

def get_google_analytics_service() -> GoogleAnalyticsService:
    """Get or create the Google Analytics service instance"""
    global _ga_service
    if _ga_service is None:
        _ga_service = GoogleAnalyticsService()
    return _ga_service

