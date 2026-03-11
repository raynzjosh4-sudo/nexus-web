#!/usr/bin/env python
import re

filepath = r'c:\nexus_websites\nexus_web\storefront\templates\storefront\shop_home.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the style block and replace it
start_marker = "    {# 2. Dynamic Theme Engine #}"
end_marker = "    {# JSON-LD Store Schema"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    before = content[:start_idx]
    after = content[end_idx:]
    
    new_style = '''    {# 2. Dynamic Theme Engine #}
    <style>
        :root {
            /* apply theme from database, fallback defaults */
            {% if theme_component %}
            --bg-page: {{ theme_component.backgroundColor|default:"#121418" }};
            --bg-card: {{ theme_component.surfaceColor|default:"#181b21" }};
            --text-main: {{ theme_component.textColor|default:"#ffffff" }};
            --text-sub: {{ theme_component.secondaryTextColor|default:"#9ca3af" }};
            --accent-color: {{ theme_component.accentColor|default:"#f97316" }};
            --secondary-color: {{ theme_component.secondaryColor|default:"#DA03D0" }};
            {% else %}
            --bg-page: #121418;
            --bg-card: #181b21;
            --text-main: #ffffff;
            --text-sub: #9ca3af;
            --accent-color: #f97316;
            --secondary-color: #DA03D0;
            {% endif %}
            --glass-border: rgba(255, 255, 255, 0.08);
        }

        /* Force variables onto the main containers */
        html,
        body,
        .main-wrapper,
        .shop-home {
            background-color: var(--bg-page) !important;
            color: var(--text-main) !important;
        }

        #view-products,
        #view-market {
            display: none;
            opacity: 0;
        }

        /* Smooth switching */
        .view-content {
            transition: opacity 0.3s ease;
        }
    </style>

    '''
    
    new_content = before + new_style + after
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("CSS section fixed successfully")
else:
    print(f"Could not find markers. start_idx={start_idx}, end_idx={end_idx}")
