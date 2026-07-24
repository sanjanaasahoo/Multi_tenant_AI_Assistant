from app.services.intent_service import Intent, DetectedIntent
from app.config import CONTACT

_C = CONTACT  # shorthand for f-string readability

_RESPONSES: dict[str, str] = {

    Intent.GREETING: (
        "Hello! Welcome to Crushaders Tech Solutions. 👋\n"
        "I'm your digital marketing assistant — here to help you explore our services, "
        "learn about the industries we work in, or find out how to reach our team.\n"
        "What can I help you with today?"
    ),

    Intent.GOODBYE: (
        "Thank you for visiting Crushaders Tech! It was great connecting with you. "
        "Whenever you're ready to grow your brand digitally, our team is here. "
        "Wishing you all the very best! 🚀"
    ),

    Intent.CONTACT_INFO: (
        "Here's how to reach the Crushaders Tech team:\n\n"
        f"📧  Email:   {_C['email']}\n"
        f"📞  Phone:   {_C['phone']}\n\n"
        f"📍  India:   {_C['india']}\n"
        f"📍  USA:     {_C['usa']}\n"
        f"📍  UK:      {_C['uk']}\n\n"
        "Our team typically responds within one business day. "
        "Is there anything specific you'd like to discuss with them?"
    ),

    Intent.FAQ_ROI: (
        "ROI measurement is central to everything we do at Crushaders Tech. "
        "We track performance through clear KPIs: website traffic growth, lead volume, "
        "conversion rates, cost-per-lead, and direct revenue attribution.\n\n"
        "For paid campaigns, you get full transparency on ad spend versus returns. "
        "For SEO, we monitor keyword rankings, organic sessions, and engagement over time. "
        "Every client receives regular performance reports so you always know exactly "
        "what your investment is delivering."
    ),

    Intent.FAQ_LOCAL_AGENCY: (
        "A local agency like Crushaders Tech brings something national agencies often can't — "
        "deep regional market knowledge, cultural understanding, and genuine personal accountability.\n\n"
        "We combine enterprise-level expertise and certifications (Google, Meta, Amazon) "
        "with the agility of a team truly invested in your success. "
        "Our track record of 1500+ clients across 20+ countries shows we deliver at both "
        "local and global scale."
    ),

    Intent.FAQ_GENERAL: (
        "Great question! Crushaders Tech is a full-service digital marketing agency. "
        "We offer services ranging from SEO and content creation to lead generation, "
        "e-commerce solutions, and reputation management.\n\n"
        "Our process begins with understanding your goals, followed by a tailored strategy "
        "and ongoing performance optimisation. "
        f"Reach us at {_C['email']} for a detailed consultation."
    ),

    Intent.CERTIFICATIONS: (
        "Yes — Crushaders Tech is certified across all major digital platforms:\n\n"
        "✅  Google Partner — Google Ads expertise and performance standards\n"
        "✅  Meta Ads Partner — Facebook and Instagram advertising\n"
        "✅  Amazon Ads Partner — Amazon marketplace advertising\n\n"
        "These certifications mean your campaigns are managed to the highest platform standards."
    ),

    Intent.CLIENTS_PORTFOLIO: (
        "We have partnered with businesses across diverse industries. Notable clients include:\n\n"
        "🏨  Mayfair Group (Hospitality)\n"
        "🏗️  Utkal Builders (Real Estate)\n"
        "🍱  Kasturi Food (F&B)\n"
        "🛒  Wefe, Urban Canteen, Delta\n"
        "💍  Lalchand Jewellers\n"
        "🏭  Alucraft, BBI\n\n"
        f"For industry-specific case details, reach out at {_C['email']}."
    ),

    Intent.AWARDS: (
        "Crushaders Tech has earned recognition from several prestigious organisations:\n\n"
        "🏆  Startup Odisha Recognition\n"
        "🏆  NASSCOM Recognition\n"
        "🏆  Brand Leadership Award\n\n"
        "These reflect our commitment to excellence and measurable results for clients "
        "across industries."
    ),

    Intent.ABOUT_COMPANY: (
        "Crushaders Tech Solutions is a full-service digital marketing agency headquartered "
        "in Bhubaneswar, Odisha, with offices in the USA and UK.\n\n"
        "📊  10+ years of experience\n"
        "👥  60+ digital marketing experts\n"
        "🌍  1500+ clients across 20+ countries\n"
        "🤝  Google, Meta & Amazon Ads certified\n\n"
        "Led by Amit Prakash Nayak (CEO) and Bidhan Pattanayak (COO), our team delivers "
        "data-driven strategies that produce real business results."
    ),

    Intent.SERVICE_SEO_BRANDING: (
        "Our Digital Branding service covers both SEO and AEO:\n\n"
        "🔍  SEO — Improves your rankings on Google and other search engines\n"
        "🤖  AEO — Ensures your brand appears in AI-powered search responses\n\n"
        "As a certified Google Partner, we build organic strategies that improve visibility, "
        "drive quality traffic, and build long-term brand authority. "
        f"Want to learn more? Reach us at {_C['email']}."
    ),

    Intent.SERVICE_CONTENT: (
        "Our Content Creation service covers all formats:\n\n"
        "✍️  Blog articles and website copy\n"
        "📱  Social media content (posts, reels, stories)\n"
        "🎥  Video scripts and production\n"
        "📊  Infographics and visual content\n\n"
        "Every piece is crafted to your brand voice and supports your SEO and marketing goals. "
        f"Get in touch at {_C['email']} to explore content packages."
    ),

    Intent.SERVICE_LEAD_GEN: (
        "Our Lead Generation service brings qualified prospects to your business through:\n\n"
        "📢  Google Ads — targeted search and display campaigns\n"
        "📘  Meta Ads — Facebook and Instagram advertising\n"
        "🛒  Amazon Ads — marketplace advertising\n"
        "🎯  Landing page optimisation and audience segmentation\n\n"
        "As certified Meta and Amazon Ads partners, we ensure your ad spend converts. "
        f"Contact our team at {_C['email']} or call {_C['phone']} to get started."
    ),

    Intent.SERVICE_ECOMMERCE: (
        "Our E-commerce Solutions service covers the full online selling journey:\n\n"
        "🏪  Store setup — Shopify, WooCommerce, or custom-built\n"
        "📦  Product page optimisation\n"
        "💳  Payment gateway integration\n"
        "📣  Traffic and conversion campaigns\n\n"
        "We handle both the technical foundation and the ongoing marketing. "
        f"Reach our team at {_C['email']} to discuss your e-commerce goals."
    ),

    Intent.SERVICE_ORM: (
        "Our Online Reputation Management (ORM) service includes:\n\n"
        "👁️  Brand monitoring across all platforms\n"
        "🛡️  Addressing and suppressing negative content\n"
        "⭐  Amplifying positive reviews and brand signals\n"
        "📈  Long-term reputation building strategy\n\n"
        "Whether you're managing a PR situation or proactively building trust, we can help. "
        f"Reach us at {_C['email']} for a confidential consultation."
    ),

    Intent.SERVICE_CELEBRITY: (
        "Our Celebrity Profile Management service is designed for public figures and influencers:\n\n"
        "📱  Social media strategy and management\n"
        "✍️  Brand storytelling and content creation\n"
        "📰  Digital PR and media presence\n"
        "🌟  Personal brand positioning\n\n"
        f"Contact us at {_C['email']} for a tailored proposal."
    ),

    Intent.SERVICE_POLITICAL: (
        "Our Political Campaign Management service covers:\n\n"
        "📣  Social media voter outreach campaigns\n"
        "🎯  Targeted digital advertising by constituency\n"
        "✍️  Campaign content creation and storytelling\n"
        "📊  Real-time campaign analytics\n\n"
        "We work with urgency and precision during campaign cycles. "
        f"Get in touch at {_C['email']} to discuss your campaign needs."
    ),

    Intent.SERVICES_GENERAL: (
        "Crushaders Tech offers 7 core digital marketing services:\n\n"
        "1.  Content Creation — blogs, videos, social media\n"
        "2.  Digital Branding & SEO/AEO — search rankings and brand identity\n"
        "3.  E-commerce Solutions — online store setup and growth\n"
        "4.  Lead Generation — targeted ads on Google, Meta, Amazon\n"
        "5.  Celebrity Profile Management — digital presence for public figures\n"
        "6.  Online Reputation Management (ORM) — brand protection\n"
        "7.  Political Campaign Management — digital strategy for elections\n\n"
        "Which one would you like to explore further?"
    ),

    Intent.INDUSTRY_HEALTHCARE: (
        "Healthcare is one of our six specialised industry verticals.\n\n"
        "We help hospitals, clinics, and healthcare brands with:\n"
        "🏥  Local SEO and patient acquisition campaigns\n"
        "⭐  Reputation management and review strategies\n"
        "✍️  Health-focused content marketing\n\n"
        f"Reach out at {_C['email']} for a tailored consultation."
    ),

    Intent.INDUSTRY_REAL_ESTATE: (
        "Real Estate is one of our core industry specialisations.\n\n"
        "We help developers, builders, and agencies with:\n"
        "🏠  Local SEO for property discovery\n"
        "🎯  Qualified lead generation campaigns\n"
        "📱  Social media presence and content\n\n"
        "We have worked with clients like Utkal Builders to deliver consistent results. "
        f"Connect with our team at {_C['email']}."
    ),

    Intent.INDUSTRY_EDUCATION: (
        "Education is one of our specialised verticals.\n\n"
        "We help schools, colleges, and ed-tech platforms with:\n"
        "🎓  Student lead generation campaigns\n"
        "🔍  SEO and content for admissions growth\n"
        "📱  Social media management and brand building\n\n"
        f"Contact us at {_C['email']} to discuss your institution's goals."
    ),

    Intent.INDUSTRY_HOSPITALITY: (
        "Hospitality and Tourism is a key industry we serve.\n\n"
        "We help hotels, resorts, and travel businesses with:\n"
        "📍  Local SEO and Google Business optimisation\n"
        "📣  Direct booking campaigns\n"
        "📱  Social media and influencer content\n\n"
        f"Contact our team at {_C['email']} for a tailored strategy."
    ),

    Intent.INDUSTRY_JEWELLERY: (
        "Jewellery and Watches is one of our specialised verticals.\n\n"
        "We help jewellery brands with:\n"
        "✨  Visual content and social media campaigns\n"
        "🔍  SEO for high-intent purchase queries\n"
        "🎯  Targeted advertising for in-store and online sales\n\n"
        f"Reach us at {_C['email']} to elevate your brand."
    ),

    Intent.INDUSTRY_MANUFACT: (
        "Manufacturing is one of the six industries we serve.\n\n"
        "We help manufacturers and industrial companies with:\n"
        "🔍  B2B SEO and content marketing\n"
        "🎯  Lead generation for enterprise buyers\n"
        "💼  LinkedIn strategy and digital presence\n\n"
        f"Contact us at {_C['email']} to discuss your requirements."
    ),

    Intent.UNKNOWN: (
        "That's a great question, but it's a little outside what I can help with here! "
        "I'm best equipped to answer questions about Crushaders Tech's services, "
        "industries, team, and contact details.\n\n"
        f"For anything more specific, email {_C['email']} "
        f"or call {_C['phone']} — our team will be happy to help."
    ),
}


def build_response(intent: DetectedIntent) -> str:
    """
    Return the response string for the detected intent.
    Falls back to UNKNOWN if intent name is not in the template map.
    """
    return _RESPONSES.get(intent.name, _RESPONSES[Intent.UNKNOWN])