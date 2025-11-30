"""
NeuroCron AI Prompt Templates
Structured prompts for each module's AI functionality
"""

from typing import List, Optional


class PromptTemplates:
    """Collection of prompt templates for AI generation tasks."""
    
    # ═══════════════════════════════════════════════════════════════════
    # TIER 1: STRATEGIC TASKS (Claude Opus 4.5)
    # ═══════════════════════════════════════════════════════════════════
    
    # === NeuroPlan: Strategy Generation ===
    
    STRATEGY_SYSTEM = """You are NeuroPlan, an elite marketing strategist AI with decades of combined expertise in digital marketing, brand building, and growth strategy.

Your strategies are:
- Data-driven and actionable, not generic advice
- Tailored to the specific business, industry, and budget
- Include specific tactics with timelines
- Measurable with clear KPIs
- Realistic given the constraints provided

You must output ONLY valid JSON, no additional text or markdown."""

    STRATEGY_USER = """Create a comprehensive {timeline_months}-month marketing strategy for:

**Business:** {business_name}
**Description:** {business_description}
**Target Audience:** {target_audience}
**Goals:** {goals}
**Budget Level:** {budget_range} (low: <$5K/mo, medium: $5-20K/mo, high: >$20K/mo)
**Focus Areas:** {focus_areas}

Generate a complete strategy as JSON:
{{
    "executive_summary": "2-3 sentence compelling overview",
    "vision": "The long-term vision statement",
    "mission": "The marketing mission statement",
    "quarterly_plans": [
        {{
            "quarter": "Q1",
            "theme": "Quarter theme (e.g., Foundation & Launch)",
            "objectives": ["Specific objective 1", "Specific objective 2", "Specific objective 3"],
            "key_initiatives": ["Initiative with details", "Another initiative", "Third initiative"],
            "budget_allocation": {{"paid_ads": 35, "content": 25, "social": 20, "email": 10, "tools": 10}},
            "kpis": ["Specific KPI with target", "Another measurable KPI"]
        }}
    ],
    "channel_strategies": [
        {{
            "channel": "Channel name (e.g., Google Ads)",
            "priority": "high/medium/low",
            "tactics": ["Specific tactic 1", "Specific tactic 2"],
            "budget_percentage": 30,
            "expected_outcomes": ["Measurable outcome 1", "Measurable outcome 2"]
        }}
    ],
    "competitor_positioning": "How to differentiate and win against competitors",
    "unique_selling_propositions": ["USP 1", "USP 2", "USP 3"],
    "messaging_framework": {{
        "primary_message": "Core message that resonates with audience",
        "supporting_messages": ["Supporting point 1", "Supporting point 2"],
        "tone": "Brand voice description",
        "key_proof_points": ["Social proof", "Data point", "Testimonial angle"]
    }},
    "success_metrics": ["Metric 1 with target", "Metric 2 with target"],
    "risks_and_mitigations": [
        {{"risk": "Specific risk", "mitigation": "How to address it"}}
    ],
    "total_budget_estimate": "Recommended budget with breakdown"
}}"""

    # === BattleStation: Competitor Analysis ===
    
    COMPETITOR_SYSTEM = """You are BattleStation, a competitive intelligence analyst specializing in marketing warfare.

Your analysis:
- Based on observable patterns and public information
- Actionable with specific counter-strategies
- Identifies both threats AND opportunities
- Provides tactical recommendations

Output ONLY valid JSON."""

    COMPETITOR_USER = """Analyze competitive positioning for:

**Our Business:** {our_business}
**Our Strengths:** {our_strengths}
**Competitor:** {competitor_name}
**Competitor Website:** {competitor_website}
**Industry:** {industry}

Generate competitive intelligence as JSON:
{{
    "competitor_overview": "Brief summary of competitor's positioning",
    "estimated_market_position": "Leader/Challenger/Niche/New entrant",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "marketing_tactics_observed": ["Tactic 1", "Tactic 2"],
    "messaging_analysis": "What messages they emphasize",
    "target_audience_overlap": "high/medium/low with explanation",
    "threat_level": "high/medium/low",
    "threat_explanation": "Why this threat level",
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "counter_strategies": [
        {{
            "strategy": "Counter-strategy name",
            "description": "How to implement",
            "expected_impact": "What you'll achieve",
            "timeline": "How long to implement"
        }}
    ],
    "key_differentiators_to_emphasize": ["Differentiator 1", "Differentiator 2"],
    "recommended_actions": ["Immediate action 1", "Short-term action", "Long-term action"]
}}"""

    # ═══════════════════════════════════════════════════════════════════
    # TIER 2: CREATIVE TASKS (GPT-4.1)
    # ═══════════════════════════════════════════════════════════════════
    
    # === BrainSpark: Creative Ideas ===
    
    IDEAS_SYSTEM = """You are BrainSpark, a creative genius specializing in breakthrough marketing campaigns.

Your ideas are:
- Innovative and memorable
- Practical to execute
- Tied to measurable outcomes
- Varied in approach (not all the same type)

Output ONLY valid JSON."""

    IDEAS_USER = """Generate {count} creative marketing ideas for:

**Campaign Goal:** {campaign_goal}
**Target Audience:** {target_audience}
**Brand Tone:** {brand_tone}
**Channels Available:** {channels}
**Budget Constraint:** {budget_constraint}

Generate ideas as JSON:
{{
    "ideas": [
        {{
            "title": "Catchy, memorable idea title",
            "category": "campaign/content/social/ad/pr/event/viral/partnership",
            "description": "Detailed description (2-3 sentences)",
            "hook": "The attention-grabbing element",
            "target_emotion": "What feeling to evoke",
            "estimated_impact": "high/medium/low",
            "difficulty": "easy/medium/hard",
            "estimated_cost": "Budget estimate",
            "timeline": "Time to implement",
            "required_resources": ["Resource 1", "Resource 2"],
            "success_metrics": ["How to measure success"],
            "example_execution": "Specific example of how to do it"
        }}
    ],
    "top_recommendation": "Which idea to start with and why",
    "combination_suggestion": "How to combine 2-3 ideas for maximum impact"
}}"""

    # === AudienceGenome: Persona Generation ===
    
    PERSONA_SYSTEM = """You are AudienceGenome, an expert in customer psychology, behavioral economics, and market segmentation.

Your personas are:
- Based on real market patterns
- Psychologically deep with motivations and fears
- Include specific behavioral triggers
- Diverse within the target market
- Actionable for marketing targeting

Output ONLY valid JSON."""

    PERSONA_USER = """Generate {count} detailed customer personas for:

**Business Type:** {business_type}
**Target Market:** {target_market}
**Products/Services:** {products_services}
**Price Point:** {price_point}

Generate personas as JSON:
{{
    "personas": [
        {{
            "name": "Descriptive name (e.g., 'Strategic Sarah - The Growth-Focused CMO')",
            "age_range": "30-40",
            "occupation": "Specific job title and company type",
            "income_level": "$100,000 - $150,000",
            "location": "Geographic and lifestyle description",
            "bio": "2-3 sentence personal narrative that brings them to life",
            "goals": ["Professional goal", "Personal goal", "Immediate goal"],
            "pain_points": ["Major frustration 1", "Daily annoyance", "Unmet need"],
            "motivations": ["What drives them professionally", "Personal motivation"],
            "fears": ["What keeps them up at night", "Risk they want to avoid"],
            "objections": ["Why they might not buy", "Concern about your product"],
            "preferred_channels": ["LinkedIn", "Email", "Podcasts"],
            "content_preferences": ["How-to guides", "Case studies", "Video tutorials"],
            "buying_triggers": ["What prompts them to purchase", "Decision trigger"],
            "buying_process": "How they evaluate and decide",
            "brand_affinity": ["Brands they admire and why"],
            "psychographic_profile": "Detailed personality, values, and lifestyle description",
            "best_messaging_angle": "The message that resonates most with this persona"
        }}
    ],
    "targeting_recommendations": [
        "Specific recommendation for reaching these personas",
        "Channel-specific advice"
    ],
    "content_strategy": "Overall content approach for these personas",
    "common_objections_to_address": ["Objection and how to overcome it"]
}}"""

    # === AdPilot: Ad Generation ===
    
    AD_SYSTEM = """You are AdPilot, a performance marketing expert specializing in high-converting ad creative.

Your ads are:
- Attention-grabbing with strong hooks
- Emotionally compelling
- Clear, single call-to-action
- Platform-optimized
- A/B test ready with real variations

Output ONLY valid JSON."""

    AD_USER = """Generate {count} ad variants for:

**Product:** {product_name}
**Description:** {product_description}
**Target Audience:** {target_audience}
**Platform:** {platform}
**Ad Type:** {ad_type}
**Goal:** {goal}
**Key Benefits:** {benefits}

Generate ads as JSON:
{{
    "variants": [
        {{
            "variant_name": "Descriptive name (e.g., 'Pain Point Hook')",
            "headline": "Compelling headline (platform-appropriate length)",
            "description": "Ad body copy (2-3 sentences max)",
            "cta": "Call to action button text",
            "image_prompt": "Detailed DALL-E style prompt for the ad image",
            "video_concept": "If video ad: brief video concept",
            "emotional_angle": "What emotion this variant targets",
            "predicted_ctr": 2.5,
            "predicted_conversion_rate": 1.8,
            "confidence_score": 0.85,
            "best_for_audience": "Which audience segment this works best for",
            "a_b_test_hypothesis": "What you're testing with this variant"
        }}
    ],
    "platform_notes": "Platform-specific optimization tips",
    "recommended_test_plan": "How to A/B test these variants",
    "budget_recommendation": "Suggested daily budget for testing"
}}"""

    # === ContentForge: Content Generation ===
    
    CONTENT_BLOG_SYSTEM = """You are ContentForge, an expert content strategist and SEO specialist.

Your content is:
- SEO-optimized with natural keyword usage
- Genuinely valuable and actionable
- Well-structured with scannable formatting
- Engaging with a consistent voice
- Includes data, examples, and insights

Output ONLY valid JSON."""

    CONTENT_BLOG_USER = """Write a blog article:

**Topic:** {topic}
**Target Audience:** {target_audience}
**Keywords:** {keywords}
**Tone:** {tone}
**Word Count:** ~{word_count} words
**Goal:** {goal}

Generate as JSON:
{{
    "title": "SEO-optimized, click-worthy title",
    "meta_description": "155-character meta description with keyword",
    "slug": "url-friendly-slug",
    "introduction": "Hook paragraph that captures attention and previews value",
    "sections": [
        {{
            "heading": "H2 section heading",
            "content": "Section content (multiple paragraphs, use \\n for line breaks)"
        }}
    ],
    "conclusion": "Summary with clear call-to-action",
    "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
    "keywords_used": ["Primary keyword", "Secondary keywords used"],
    "internal_link_suggestions": ["Related topics to link to"],
    "external_source_suggestions": ["Types of sources to cite"],
    "estimated_read_time": "X min read",
    "content_upgrades": ["Lead magnet ideas related to this content"]
}}"""

    # ═══════════════════════════════════════════════════════════════════
    # TIER 3: STANDARD TASKS (Llama 3.1 - FREE)
    # ═══════════════════════════════════════════════════════════════════
    
    # === Social Post Generation ===
    
    SOCIAL_SYSTEM = """You are a social media expert. Create engaging, platform-optimized posts.
Output ONLY valid JSON."""

    SOCIAL_USER = """Create {count} social posts for:

**Platform:** {platform}
**Topic:** {topic}
**Goal:** {goal}
**Brand Voice:** {brand_voice}

Generate as JSON:
{{
    "posts": [
        {{
            "content": "Post content with appropriate emojis",
            "hashtags": ["#relevant", "#hashtags"],
            "best_posting_time": "Day and time suggestion",
            "media_suggestion": "What visual would work",
            "engagement_hook": "Why this drives engagement"
        }}
    ]
}}"""

    # === Email Generation ===
    
    EMAIL_SYSTEM = """You are an email marketing expert. Write emails that get opened and clicked.
Output ONLY valid JSON."""

    EMAIL_USER = """Write an email:

**Type:** {email_type}
**Goal:** {goal}
**Audience:** {audience}
**Key Message:** {key_message}

Generate as JSON:
{{
    "subject_line": "Compelling subject",
    "preview_text": "Preview text",
    "subject_variations": ["Alt 1", "Alt 2"],
    "body": "Email body with formatting",
    "cta_text": "Button text",
    "ps_line": "Optional PS"
}}"""

    # === Translation ===
    
    TRANSLATION_SYSTEM = """You are a localization expert. Adapt content culturally, not just literally.
Output ONLY valid JSON."""

    TRANSLATION_USER = """Translate:

**From:** {source_language}
**To:** {target_language}
**Type:** {content_type}
**Content:** {content}

Generate as JSON:
{{
    "translated_content": "Localized translation",
    "cultural_notes": ["What was adapted"],
    "confidence": 0.95
}}"""

    # ═══════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    @classmethod
    def get_strategy_prompt(
        cls,
        business_name: str,
        business_description: str,
        target_audience: str,
        goals: List[str],
        budget_range: str,
        timeline_months: int = 12,
        focus_areas: Optional[List[str]] = None,
    ) -> tuple[str, str]:
        """Get strategy generation prompts (Tier 1: Strategic)."""
        user_prompt = cls.STRATEGY_USER.format(
            timeline_months=timeline_months,
            business_name=business_name,
            business_description=business_description,
            target_audience=target_audience,
            goals=", ".join(goals),
            budget_range=budget_range,
            focus_areas=", ".join(focus_areas) if focus_areas else "All channels",
        )
        return cls.STRATEGY_SYSTEM, user_prompt
    
    @classmethod
    def get_ideas_prompt(
        cls,
        campaign_goal: str,
        target_audience: str,
        brand_tone: str,
        channels: List[str],
        count: int = 5,
        budget_constraint: str = "moderate",
    ) -> tuple[str, str]:
        """Get creative ideas prompts (Tier 2: Creative)."""
        user_prompt = cls.IDEAS_USER.format(
            count=count,
            campaign_goal=campaign_goal,
            target_audience=target_audience,
            brand_tone=brand_tone,
            channels=", ".join(channels),
            budget_constraint=budget_constraint,
        )
        return cls.IDEAS_SYSTEM, user_prompt
    
    @classmethod
    def get_persona_prompt(
        cls,
        business_type: str,
        target_market: str,
        products_services: str,
        count: int = 3,
        price_point: str = "mid-range",
    ) -> tuple[str, str]:
        """Get persona generation prompts (Tier 2: Creative)."""
        user_prompt = cls.PERSONA_USER.format(
            count=count,
            business_type=business_type,
            target_market=target_market,
            products_services=products_services,
            price_point=price_point,
        )
        return cls.PERSONA_SYSTEM, user_prompt
    
    @classmethod
    def get_ad_prompt(
        cls,
        product_name: str,
        product_description: str,
        target_audience: str,
        platform: str,
        ad_type: str,
        goal: str,
        count: int = 3,
        benefits: str = "",
    ) -> tuple[str, str]:
        """Get ad generation prompts (Tier 2: Creative)."""
        user_prompt = cls.AD_USER.format(
            count=count,
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience,
            platform=platform,
            ad_type=ad_type,
            goal=goal,
            benefits=benefits or "Not specified",
        )
        return cls.AD_SYSTEM, user_prompt
    
    @classmethod
    def get_blog_prompt(
        cls,
        topic: str,
        target_audience: str,
        keywords: List[str],
        tone: str = "professional",
        word_count: int = 1500,
        goal: str = "educate and convert",
    ) -> tuple[str, str]:
        """Get blog content prompts (Tier 2: Creative)."""
        user_prompt = cls.CONTENT_BLOG_USER.format(
            topic=topic,
            target_audience=target_audience,
            keywords=", ".join(keywords),
            tone=tone,
            word_count=word_count,
            goal=goal,
        )
        return cls.CONTENT_BLOG_SYSTEM, user_prompt
    
    @classmethod
    def get_social_prompt(
        cls,
        platform: str,
        topic: str,
        goal: str,
        brand_voice: str,
        count: int = 5,
    ) -> tuple[str, str]:
        """Get social post prompts (Tier 3: Standard - FREE)."""
        user_prompt = cls.SOCIAL_USER.format(
            count=count,
            platform=platform,
            topic=topic,
            goal=goal,
            brand_voice=brand_voice,
        )
        return cls.SOCIAL_SYSTEM, user_prompt
    
    @classmethod
    def get_email_prompt(
        cls,
        email_type: str,
        goal: str,
        audience: str,
        key_message: str,
    ) -> tuple[str, str]:
        """Get email prompts (Tier 3: Standard - FREE)."""
        user_prompt = cls.EMAIL_USER.format(
            email_type=email_type,
            goal=goal,
            audience=audience,
            key_message=key_message,
        )
        return cls.EMAIL_SYSTEM, user_prompt
    
    @classmethod
    def get_translation_prompt(
        cls,
        source_language: str,
        target_language: str,
        content_type: str,
        content: str,
    ) -> tuple[str, str]:
        """Get translation prompts (Tier 3: Standard - FREE)."""
        user_prompt = cls.TRANSLATION_USER.format(
            source_language=source_language,
            target_language=target_language,
            content_type=content_type,
            content=content,
        )
        return cls.TRANSLATION_SYSTEM, user_prompt
    
    @classmethod
    def get_competitor_prompt(
        cls,
        our_business: str,
        our_strengths: str,
        competitor_name: str,
        competitor_website: str,
        industry: str,
    ) -> tuple[str, str]:
        """Get competitor analysis prompts (Tier 1: Strategic)."""
        user_prompt = cls.COMPETITOR_USER.format(
            our_business=our_business,
            our_strengths=our_strengths,
            competitor_name=competitor_name,
            competitor_website=competitor_website,
            industry=industry,
        )
        return cls.COMPETITOR_SYSTEM, user_prompt
