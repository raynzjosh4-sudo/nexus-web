// SEO Helpers Module
console.log('seo-helpers.js loaded');

// Helper functions for SEO and data processing
const SEOHelpers = {
    generateMetaTags: (title, description, imageUrl) => {
        // Generate meta tags for social sharing
        return {
            title,
            description,
            imageUrl
        };
    },

    trackEvent: (category, action, label) => {
        // Track events for analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label
            });
        }
    }
};

window.SEOHelpers = SEOHelpers;
