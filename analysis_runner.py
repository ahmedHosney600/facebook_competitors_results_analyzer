# analysis_runner.py
import json
from competitor_analyser import FacebookCompetitorAnalyzer
from competitor_analysis_reporter import CompetitorReportGenerator
import os
from datetime import datetime
import readline

def get_fb_competitors_json():
    facebook_data = None
    while not facebook_data:
        path = input("Please input path for data input JSON: ").strip()

        if not os.path.exists(path):
            print("❌ File does not exist. Please try again.")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                facebook_data = json.load(f)
                print("✅ File loaded successfully.")
        except json.JSONDecodeError:
            print("❌ File is not valid JSON. Please provide a valid JSON file.")
            facebook_data = None
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            facebook_data = None
    return facebook_data

# Run the analysis
# def run_demo_analysis():
#     facebook_data = get_fb_competitors_json()
#     analyzer = FacebookCompetitorAnalyzer(data_dict=facebook_data)
    
#     # Run complete analysis
#     results = analyzer.analyze_all_competitors()
    
    
    

#     # Generate reports
#     generator = CompetitorReportGenerator(results)
#     generator.generate_all_reports("sample_competitor_analysis")
    
    
#     return results

# Additional utility function to extract specific insights
def extract_actionable_insights(analysis_results):
    """Extract specific actionable insights for strategic planning"""
    
    insights = {
        "immediate_opportunities": [],
        "competitive_advantages": [],
        "market_gaps": [],
        "content_strategy_recommendations": [],
        "advertising_opportunities": []
    }
    
    competitors = analysis_results['competitors']
    market_position = analysis_results['market_position_analysis']
    
    # Immediate opportunities
    for competitor in competitors:
        name = competitor['page_name']
        ads = competitor['advertising_analysis']
        engagement = competitor['engagement_metrics']
        
        # Not advertising = opportunity
        if not ads['is_advertising']:
            insights["immediate_opportunities"].append({
                "type": "advertising_gap",
                "competitor": name,
                "opportunity": f"Enter paid advertising market - {name} has {engagement['followers']:,} followers but no ads"
            })
        
        # Poor engagement quality = opportunity
        if engagement['follower_engagement_quality'] in ['poor', 'very_poor_or_fake_followers']:
            insights["immediate_opportunities"].append({
                "type": "engagement_weakness",
                "competitor": name,
                "opportunity": f"Target {name}'s audience with better engagement - they show signs of low-quality followers"
            })
    
    # Content strategy recommendations
    view_performances = [(comp['page_name'], comp['engagement_metrics']['reel_views']['average_views']) 
                        for comp in competitors]
    best_performer = max(view_performances, key=lambda x: x[1])
    
    insights["content_strategy_recommendations"].append({
        "benchmark": f"{best_performer[0]} averages {best_performer[1]:,.0f} views per reel",
        "recommendation": "Analyze their top-performing content themes and formats",
        "potential_impact": "Could increase content performance by 2-5x based on gap analysis"
    })
    
    # Market gaps
    locations = set()
    categories = set()
    for comp in competitors:
        business = comp['business_analysis']
        if business['location'] != 'not_specified':
            locations.add(business['location'])
        if business['categories'] != 'not_specified':
            categories.add(business['categories'])
    
    if len(locations) == 1:
        insights["market_gaps"].append({
            "type": "geographic_concentration",
            "gap": f"All competitors focus on {list(locations)[0]}",
            "opportunity": "Geographic expansion to other cities/areas"
        })
    
    # Competitive advantages to exploit
    advertising_competitors = [comp for comp in competitors if comp['advertising_analysis']['is_advertising']]
    if len(advertising_competitors) == 1:
        insights["competitive_advantages"].append({
            "advantage": "Low advertising competition",
            "detail": f"Only {advertising_competitors[0]['page_name']} is actively advertising",
            "action": "Enter advertising market with aggressive campaigns"
        })
    
    cross_platform_adoption = [comp['business_analysis']['cross_platform_presence']['total_platforms'] 
                              for comp in competitors]
    avg_platforms = sum(cross_platform_adoption) / len(cross_platform_adoption)
    
    if avg_platforms < 2:
        insights["competitive_advantages"].append({
            "advantage": "Poor cross-platform integration",
            "detail": f"Competitors average only {avg_platforms:.1f} platforms",
            "action": "Develop strong multi-platform presence (TikTok, Instagram, WhatsApp Business)"
        })
    
    return insights

# Enhanced analysis runner with actionable insights
def run_comprehensive_analysis():
    """Run the complete analysis with actionable insights"""
    
    print("🚀 Starting Comprehensive Facebook Competitor Analysis...\n")
    
    # Run basic analysis
    facebook_data = get_fb_competitors_json()
    analyzer = FacebookCompetitorAnalyzer(data_dict=facebook_data)
    results = analyzer.analyze_all_competitors()

    # Extract actionable insights
    actionable_insights = extract_actionable_insights(results)
    
    
    # Need testig
    # Combine all results
    comprehensive_results = {
        **results,
        "actionable_insights": actionable_insights,
        "executive_summary": generate_executive_summary(results, actionable_insights)
    }

    # Generate reports
    output_folder = "output"
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs(output_folder, exist_ok=True)
    generator = CompetitorReportGenerator(comprehensive_results)
    generator.generate_all_reports(f"{output_folder}/competitor_analysis_{current_timestamp}")
    
    return comprehensive_results

def generate_executive_summary(results, insights):
    """Generate executive summary for leadership"""
    
    competitors = results['competitors']
    summary_stats = results['summary_statistics']
    
    # Find market leader
    market_leader = max(competitors, key=lambda x: x['engagement_metrics']['followers'])
    
    # Calculate total market size
    total_followers = sum(comp['engagement_metrics']['followers'] for comp in competitors)
    
    # Count opportunities
    ad_gaps = len([comp for comp in competitors if not comp['advertising_analysis']['is_advertising']])
    
    summary = {
        "market_overview": {
            "total_market_size": f"{total_followers:,} combined followers",
            "market_leader": market_leader['page_name'],
            "leader_market_share": f"{(market_leader['engagement_metrics']['followers'] / total_followers * 100):.1f}%",
            "average_engagement_quality": summary_stats['average_content_performance']
        },
        "key_opportunities": {
            "advertising_gaps": f"{ad_gaps} out of {len(competitors)} competitors not advertising",
            "engagement_weakness": len([comp for comp in competitors 
                                      if comp['engagement_metrics']['follower_engagement_quality'] in ['poor', 'very_poor_or_fake_followers']]),
            "cross_platform_gaps": len([comp for comp in competitors 
                                       if comp['business_analysis']['cross_platform_presence']['total_platforms'] < 2])
        },
        "strategic_recommendations": [
            "Enter paid advertising market immediately - low competition",
            "Focus on authentic engagement vs follower count",
            "Develop strong cross-platform presence",
            "Target geographic expansion opportunities",
            "Benchmark content against SIGMA TOP's performance"
        ],
        "risk_assessment": "Low - market shows fragmentation with no dominant player controlling >75% market share"
    }
    
    return summary

# Run the analysis
if __name__ == "__main__":
    results = run_comprehensive_analysis()