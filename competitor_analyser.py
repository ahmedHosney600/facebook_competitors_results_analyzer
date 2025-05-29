# competitor_analyser.py
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import re

class FacebookCompetitorAnalyzer:
    def __init__(self, data_file_path: str = None, data_dict: dict = None):
        """Initialize with either file path or data dictionary"""
        if data_dict:
            self.data = data_dict
        elif data_file_path:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise ValueError("Either data_file_path or data_dict must be provided")
        
    # def convert_to_number(self, value: str) -> int:
    #     """Convert string numbers with K suffix to integers"""
    #     if not value or value == "":
    #         return 0
        
    #     value = str(value).upper().replace(',', '')
    #     if 'K' in value:
    #         return int(float(value.replace('K', '')) * 1000)
    #     return int(value)
    def convert_to_number(self, value: str) -> int:
        """
        Convert string numbers with suffixes like k, m, b, t to integers.
        Handles both uppercase and lowercase suffixes.
        """
        if not value or not isinstance(value, str):
            return 0

        value = value.strip().replace(',', '')
        suffixes = {
            'k': 1_000,
            'm': 1_000_000,
            'b': 1_000_000_000,
            't': 1_000_000_000_000
        }

        last_char = value[-1].lower()
        if last_char in suffixes:
            try:
                num = float(value[:-1])
                return int(num * suffixes[last_char])
            except ValueError:
                return 0
        else:
            try:
                return int(float(value))
            except ValueError:
                return 0

    def extract_views_number(self, views_str: str) -> int:
        """Extract numeric views from string using convert_to_number"""
        return self.convert_to_number(views_str)

    
    def calculate_engagement_metrics(self, page_data: dict) -> dict:
        """Calculate various engagement metrics"""
        likes = self.convert_to_number(page_data.get('likes', 0))
        followers = self.convert_to_number(page_data.get('followers', 0))
        
        # Reel performance analysis
        reels = page_data.get('top_reels', [])
        reel_views = [self.extract_views_number(reel.get('views', '0')) for reel in reels]
        
        engagement_metrics = {
            'likes': likes,
            'followers': followers,
            'like_to_follower_ratio': round(likes / followers * 100, 2) if followers > 0 else 0,
            'follower_engagement_quality': self.assess_engagement_quality(likes, followers),
            'total_reels': len(reels),
            'reel_views': {
                'total_views': sum(reel_views),
                'average_views': round(statistics.mean(reel_views), 2) if reel_views else 0,
                'median_views': statistics.median(reel_views) if reel_views else 0,
                'max_views': max(reel_views) if reel_views else 0,
                'min_views': min(reel_views) if reel_views else 0,
                'views_distribution': reel_views
            },
            'content_performance_score': self.calculate_content_score(reel_views, followers)
        }
        
        return engagement_metrics
    
    def assess_engagement_quality(self, likes: int, followers: int) -> str:
        """Assess the quality of engagement based on like-to-follower ratio"""
        if followers == 0:
            return "insufficient_data"
        
        ratio = likes / followers
        if ratio > 0.9:
            return "excellent"
        elif ratio > 0.7:
            return "good"
        elif ratio > 0.5:
            return "average"
        elif ratio > 0.2:
            return "poor"
        else:
            return "very_poor_or_fake_followers"
    
    def calculate_content_score(self, views: List[int], followers: int) -> float:
        """Calculate content performance score based on views vs followers"""
        if not views or followers == 0:
            return 0.0
        
        avg_views = statistics.mean(views)
        score = (avg_views / followers) * 100 if followers > 0 else 0
        return round(score, 2)
    
    def analyze_business_info(self, page_data: dict) -> dict:
        """Analyze business information and setup"""
        about_info = page_data.get('about_info', {})
        
        contact_methods = []
        if about_info.get('Mobile'):
            contact_methods.append('phone')
        if about_info.get('WhatsApp'):
            contact_methods.append('whatsapp')
        if about_info.get('TikTok'):
            contact_methods.append('tiktok')
        if about_info.get('Tumblr'):
            contact_methods.append('tumblr')
        
        return {
            'categories': about_info.get('Categories', 'not_specified'),
            'location': about_info.get('Address', 'not_specified'),
            'contact_methods': contact_methods,
            'contact_diversity_score': len(contact_methods),
            'business_hours': about_info.get('Hours', 'not_specified'),
            'cross_platform_presence': self.analyze_cross_platform(about_info),
            'business_maturity': self.assess_business_maturity(about_info)
        }
    
    def analyze_cross_platform(self, about_info: dict) -> dict:
        """Analyze cross-platform presence"""
        platforms = {
            'tiktok': bool(about_info.get('TikTok')),
            'whatsapp_business': bool(about_info.get('WhatsApp')),
            'tumblr': bool(about_info.get('Tumblr'))
        }
        
        return {
            'platforms': platforms,
            'total_platforms': sum(platforms.values()),
            'integration_score': sum(platforms.values()) / len(platforms) * 100
        }
    
    def assess_business_maturity(self, about_info: dict) -> str:
        """Assess business maturity based on available information"""
        maturity_indicators = 0
        
        if about_info.get('Address') and about_info.get('Address') != 'not_specified':
            maturity_indicators += 1
        if about_info.get('Mobile'):
            maturity_indicators += 1
        if about_info.get('Hours'):
            maturity_indicators += 1
        if about_info.get('Categories'):
            maturity_indicators += 1
        
        if maturity_indicators >= 3:
            return "mature"
        elif maturity_indicators >= 2:
            return "developing"
        else:
            return "basic"
    
    def analyze_advertising_strategy(self, ads_data: dict) -> dict:
        """Analyze advertising strategy and investment"""
        total_ads = ads_data.get('total_active_ads', 0)
        active_ads = ads_data.get('active_ads', [])
        
        ad_analysis = {
            'is_advertising': total_ads > 0,
            'total_active_ads': total_ads,
            'advertising_intensity': self.categorize_ad_intensity(total_ads),
            'ad_strategies': [],
            'cta_types': [],
            'ad_messaging_themes': []
        }
        
        for ad in active_ads:
            # Analyze CTA
            cta = ad.get('cta', '').lower()
            if cta and cta not in ad_analysis['cta_types']:
                ad_analysis['cta_types'].append(cta)
            
            # Analyze messaging themes
            description = ad.get('ad_description', '').lower()
            themes = self.extract_messaging_themes(description)
            ad_analysis['ad_messaging_themes'].extend(themes)
        
        ad_analysis['ad_messaging_themes'] = list(set(ad_analysis['ad_messaging_themes']))
        
        return ad_analysis
    
    def categorize_ad_intensity(self, total_ads: int) -> str:
        """Categorize advertising intensity"""
        if total_ads == 0:
            return "no_advertising"
        elif total_ads <= 2:
            return "light"
        elif total_ads <= 5:
            return "moderate"
        else:
            return "heavy"
    
    def extract_messaging_themes(self, description: str) -> List[str]:
        """Extract messaging themes from ad descriptions"""
        themes = []
        
        # Price-related keywords
        price_keywords = ['price', 'cheap', 'affordable', 'discount', 'offer', 'deal']
        if any(keyword in description for keyword in price_keywords):
            themes.append('price_focused')
        
        # Quality keywords
        quality_keywords = ['quality', 'premium', 'best', 'top', 'excellent']
        if any(keyword in description for keyword in quality_keywords):
            themes.append('quality_focused')
        
        # Service keywords
        service_keywords = ['service', 'support', 'help', 'consultation']
        if any(keyword in description for keyword in service_keywords):
            themes.append('service_focused')
        
        # Product keywords
        product_keywords = ['product', 'design', 'modern', 'new']
        if any(keyword in description for keyword in product_keywords):
            themes.append('product_focused')
        
        return themes
    
    def calculate_market_position(self, all_competitors: List[dict]) -> dict:
        """Calculate market position relative to competitors"""
        followers_list = [comp['engagement_metrics']['followers'] for comp in all_competitors]
        views_list = [comp['engagement_metrics']['reel_views']['average_views'] for comp in all_competitors]
        
        market_analysis = {}
        
        for i, competitor in enumerate(all_competitors):
            followers = competitor['engagement_metrics']['followers']
            avg_views = competitor['engagement_metrics']['reel_views']['average_views']
            
            # Market share approximation based on followers
            total_followers = sum(followers_list)
            market_share = (followers / total_followers * 100) if total_followers > 0 else 0
            
            # Ranking
            follower_rank = sorted(followers_list, reverse=True).index(followers) + 1
            engagement_rank = sorted(views_list, reverse=True).index(avg_views) + 1
            
            market_analysis[competitor['page_name']] = {
                'estimated_market_share': round(market_share, 2),
                'follower_rank': follower_rank,
                'engagement_rank': engagement_rank,
                'overall_competitiveness': self.calculate_competitiveness_score(competitor)
            }
        
        return market_analysis
    
    def calculate_competitiveness_score(self, competitor_data: dict) -> float:
        """Calculate overall competitiveness score"""
        metrics = competitor_data['engagement_metrics']
        business = competitor_data['business_analysis']
        ads = competitor_data['advertising_analysis']
        
        # Scoring components (0-100 scale)
        follower_score = min(metrics['followers'] / 1000 * 10, 100)  # Max at 10K followers
        engagement_score = min(metrics['content_performance_score'], 100)
        business_maturity_scores = {'basic': 20, 'developing': 60, 'mature': 100}
        business_score = business_maturity_scores.get(business['business_maturity'], 0)
        advertising_score = 100 if ads['is_advertising'] else 0
        
        # Weighted average
        total_score = (
            follower_score * 0.3 +
            engagement_score * 0.3 +
            business_score * 0.2 +
            advertising_score * 0.2
        )
        
        return round(total_score, 2)
    
    def generate_competitive_insights(self, market_position: dict, all_competitors: List[dict]) -> dict:
        """Generate actionable competitive insights"""
        insights = {
            'market_leader': max(market_position.items(), key=lambda x: x[1]['estimated_market_share']),
            'engagement_leader': max(market_position.items(), key=lambda x: x[1]['overall_competitiveness']),
            'advertising_gap': [],
            'content_opportunities': [],
            'market_gaps': []
        }
        
        # Find advertising gaps
        for competitor in all_competitors:
            if not competitor['advertising_analysis']['is_advertising']:
                insights['advertising_gap'].append(competitor['page_name'])
        
        # Content performance analysis
        avg_performance = statistics.mean([
            comp['engagement_metrics']['content_performance_score'] for comp in all_competitors
        ])
        
        for competitor in all_competitors:
            if competitor['engagement_metrics']['content_performance_score'] < avg_performance:
                insights['content_opportunities'].append({
                    'competitor': competitor['page_name'],
                    'performance_gap': round(avg_performance - competitor['engagement_metrics']['content_performance_score'], 2)
                })
        
        return insights
    
    def analyze_all_competitors(self) -> dict:
        """Main analysis function that processes all competitors"""
        pages = self.data.get('pages', [])
        competitors_analysis = []
        
        # Analyze each competitor
        for page in pages:
            # if "page_name" not in page:
            #     print(page)
            competitor_data = {
                'page_name': page['page_name'] if 'page_name' in page else page['extraction_data']['page_name'],
                'page_url': page['page_url'] if 'page_url' in page else page['source_urls']['base_url'],
                'extraction_data': page['extraction_data'],
                'engagement_metrics': self.calculate_engagement_metrics(page['extraction_data']),
                'business_analysis': self.analyze_business_info(page['extraction_data']),
                'advertising_analysis': self.analyze_advertising_strategy(page.get('ads_data', {}))
            }
            competitors_analysis.append(competitor_data)
        
        # Calculate market positions
        market_position = self.calculate_market_position(competitors_analysis)
        
        # Generate insights
        competitive_insights = self.generate_competitive_insights(market_position, competitors_analysis)
        
        # Compile final analysis
        final_analysis = {
            'analysis_metadata': {
                'extraction_timestamp': self.data.get('extraction_timestamp'),
                'total_competitors': len(competitors_analysis),
                'analysis_date': datetime.now().isoformat()
            },
            'competitors': competitors_analysis,
            'market_position_analysis': market_position,
            'competitive_insights': competitive_insights,
            'summary_statistics': self.generate_summary_stats(competitors_analysis)
        }
        
        return final_analysis
    
    def generate_summary_stats(self, competitors: List[dict]) -> dict:
        """Generate summary statistics across all competitors"""
        followers_list = [comp['engagement_metrics']['followers'] for comp in competitors]
        views_list = [comp['engagement_metrics']['reel_views']['average_views'] for comp in competitors]
        
        return {
            'total_combined_followers': sum(followers_list),
            'average_followers': round(statistics.mean(followers_list), 2),
            'average_content_performance': round(statistics.mean([
                comp['engagement_metrics']['content_performance_score'] for comp in competitors
            ]), 2),
            'advertising_adoption_rate': round(sum([
                1 for comp in competitors if comp['advertising_analysis']['is_advertising']
            ]) / len(competitors) * 100, 2),
            'cross_platform_adoption': round(statistics.mean([
                comp['business_analysis']['cross_platform_presence']['total_platforms'] for comp in competitors
            ]), 2)
        }

# Usage example
def main():
    # Sample usage with your data
    sample_data = {
        "total_pages": 3,
        "extraction_timestamp": "2025-05-27T11:55:04.473391",
        "pages": [
            # Your actual data would go here
        ]
    }
    
    # Initialize analyzer
    analyzer = FacebookCompetitorAnalyzer(data_dict=sample_data)
    
    # Run complete analysis
    analysis_results = analyzer.analyze_all_competitors()
    
    # Output to JSON file
    with open('competitor_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print("Analysis complete! Results saved to competitor_analysis_results.json")
    return analysis_results

if __name__ == "__main__":
    main()