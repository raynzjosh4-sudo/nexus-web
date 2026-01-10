import os

profile_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ user.name|default:"My Profile" }} | {{ business.business_name }}</title>

    <!-- Load Global Theme & Reset -->
    {% include "storefront/theme_css.html" %}

    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>
        :root {
            /* Dynamic Theme Mapping from ProfileWebsiteThemeComponent */
            --bg-page: {{ business.theme_component.backgroundColor|default:"#0D062C" }};
            --bg-card: {{ business.theme_component.surfaceColor|default:"#181b21" }};
            --text-main: {{ business.theme_component.textColor|default:"#ffffff" }};
            --text-sub: {{ business.theme_component.secondaryTextColor|default:"#9ca3af" }};
            --accent-color: {{ business.theme_component.primaryColor|default:business.theme_component.accentColor|default:"#22d5ff" }};
            --secondary-color: {{ business.theme_component.secondaryColor|default:"#DA03D0" }};
            --glass-border: rgba(255, 255, 255, 0.08);
            --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        html, body, .profile-wrapper {
            background-color: var(--bg-page) !important;
            color: var(--text-main) !important;
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .profile-wrapper {
            max-width: 1280px;
            margin: 0 auto;
            padding: 40px 24px 120px 24px;
        }

        /* --- HERO SECTION --- */
        .premium-hero {
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 32px;
            padding: 48px;
            display: grid;
            grid-template-columns: auto 1fr auto;
            align-items: center;
            gap: 40px;
            margin-bottom: 64px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 40px 100px rgba(0,0,0,0.2);
            backdrop-filter: blur(20px);
        }

        .premium-hero::before {
            content: "";
            position: absolute;
            top: -50%;
            right: -20%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, var(--accent-color) 0%, transparent 70%);
            filter: blur(150px);
            opacity: 0.15;
            z-index: 0;
        }

        .hero-avatar-belt {
            position: relative;
            z-index: 1;
        }

        .profile-portrait {
            width: 160px;
            height: 160px;
            border-radius: 48px;
            object-fit: cover;
            border: 6px solid var(--bg-page);
            box-shadow: 0 0 0 3px var(--accent-color);
            background: var(--bg-page);
            transition: var(--transition-smooth);
        }

        .profile-portrait:hover {
            transform: scale(1.05) rotate(2deg);
        }

        .hero-info-belt {
            position: relative;
            z-index: 1;
        }

        .hero-info-belt h1 {
            font-size: 3rem;
            font-weight: 900;
            margin: 0 0 12px 0;
            letter-spacing: -2px;
            line-height: 1;
            background: linear-gradient(to bottom right, #fff 30%, var(--accent-color));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-info-belt p {
            font-size: 1.25rem;
            color: var(--text-sub);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .hero-actions-belt {
            display: flex;
            flex-direction: column;
            gap: 16px;
            z-index: 10;
        }

        .btn-modern {
            padding: 16px 32px;
            border-radius: 16px;
            font-weight: 700;
            text-decoration: none;
            transition: var(--transition-smooth);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            font-size: 0.95rem;
            border: 1px solid transparent;
        }

        .btn-ghost {
            background: rgba(255, 255, 255, 0.03);
            border-color: var(--glass-border);
            color: var(--text-main);
        }

        .btn-ghost:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .btn-danger-ghost {
            background: rgba(239, 68, 68, 0.05);
            color: #ef4444;
            border-color: rgba(239, 68, 68, 0.1);
        }

        .btn-danger-ghost:hover {
            background: #ef4444;
            color: #fff;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
        }

        /* --- DASHBOARD GRID --- */
        .profile-grid-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 48px;
        }

        /* --- SECTION STYLING --- */
        .block-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
        }

        .block-title {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .title-icon {
            width: 48px;
            height: 48px;
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-color);
            font-size: 1.2rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        /* --- ORDERS COLUMN --- */
        .order-stream {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .item-card {
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            transition: var(--transition-smooth);
            position: relative;
        }

        .item-card:hover {
            border-color: var(--accent-color);
            transform: translateX(10px);
            background: rgba(255, 255, 255, 0.02);
            box-shadow: -10px 0 30px rgba(0,0,0,0.1);
        }

        .item-preview {
            width: 100px;
            height: 100px;
            border-radius: 18px;
            object-fit: cover;
            background: #23262d;
            border: 1px solid var(--glass-border);
        }

        .item-content {
            flex: 1;
        }

        .item-tag {
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--accent-color);
            margin-bottom: 8px;
            display: block;
        }

        .item-name {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 8px;
            display: block;
        }

        .item-meta {
            font-size: 0.9rem;
            color: var(--text-sub);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .status-pill {
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-pending { background: rgba(245, 158, 11, 0.1); color: #fbbf24; }
        .status-completed { background: rgba(34, 197, 94, 0.1); color: #4ade80; }
        .status-cancelled { background: rgba(239, 68, 68, 0.1); color: #f87171; }

        .item-price-tag {
            font-size: 1.25rem;
            font-weight: 800;
            text-align: right;
        }

        /* --- WISHLIST COLUMN --- */
        .wishlist-masonry {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }

        .wish-brick {
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            transition: var(--transition-smooth);
        }

        .wish-brick:hover {
            border-color: var(--accent-color);
            transform: translateY(-12px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }

        .brick-img-wrap {
            position: relative;
            padding-top: 110%;
            overflow: hidden;
        }

        .brick-img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s ease;
        }

        .wish-brick:hover .brick-img {
            transform: scale(1.1);
        }

        .brick-body {
            padding: 20px;
        }

        .brick-name {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }

        .brick-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brick-price {
            color: var(--accent-color);
            font-weight: 800;
            font-size: 1.1rem;
        }

        .brick-icon {
            color: var(--text-sub);
            font-size: 0.9rem;
        }

        /* --- EMPTY STATES --- */
        .empty-canvas {
            background: rgba(255,255,255,0.01);
            border: 2px dashed var(--glass-border);
            border-radius: 32px;
            padding: 60px 40px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }

        .empty-icon-wrap {
            width: 80px;
            height: 80px;
            border-radius: 24px;
            background: rgba(255,255,255,0.03);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: var(--text-sub);
            opacity: 0.5;
        }

        .empty-canvas p {
            color: var(--text-sub);
            margin: 0;
            font-size: 1.1rem;
        }

        /* --- DEBUG PANEL --- */
        .debug-panel {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #000;
            color: #0f0;
            font-family: monospace;
            padding: 10px;
            border-radius: 8px;
            font-size: 10px;
            z-index: 1000;
            opacity: 0.8;
            pointer-events: none;
        }

        /* --- RESPONSIVENESS --- */
        @media (max-width: 1100px) {
            .profile-grid-layout { grid-template-columns: 1fr; gap: 64px; }
        }

        @media (max-width: 900px) {
            .premium-hero {
                grid-template-columns: 1fr;
                padding: 40px;
                text-align: center;
                gap: 24px;
            }
            .hero-actions-belt { flex-direction: row; justify-content: center; }
            .profile-portrait { width: 120px; height: 120px; }
            .hero-info-belt h1 { font-size: 2.25rem; }
        }

        @media (max-width: 600px) {
            .profile-wrapper { padding: 24px 16px; }
            .premium-hero { border-radius: 24px; padding: 32px; }
            .hero-actions-belt { flex-direction: column; width: 100%; }
            .btn-modern { width: 100%; }
            .item-card { flex-direction: column; align-items: flex-start; gap: 16px; text-align: left; }
            .item-preview { width: 100%; height: 200px; }
            .item-price-tag { width: 100%; text-align: left; padding-top: 16px; border-top: 1px solid var(--glass-border); }
            .wishlist-masonry { grid-template-columns: repeat(2, 1fr); gap: 12px; }
            .brick-body { padding: 12px; }
            .brick-name { font-size: 0.9rem; }
            .brick-price { font-size: 1rem; }
        }
    </style>
</head>

<body>

    {% include "storefront/partials/navbar.html" %}

    <div class="profile-wrapper">
        
        <!-- Premium Hero Section -->
        <div class="premium-hero" id="profile-hero">
            <div class="hero-avatar-belt">
                <img src="{{ user.avatar_url|default:'https://api.dicebear.com/7.x/avataaars/svg?seed='|add:user.name }}" class="profile-portrait" alt="User Avatar">
            </div>
            <div class="hero-info-belt">
                <h1>{{ user.name|default:"Nexus User" }}</h1>
                <p><i class="far fa-envelope"></i> {{ user.email }}</p>
                {% if user.phone_number %}
                <p style="margin-top: 8px;"><i class="fas fa-phone-alt"></i> {{ user.phone_number }}</p>
                {% endif %}
            </div>
            <div class="hero-actions-belt">
                <a href="{% url 'shop_home' %}" class="btn-modern btn-ghost">
                    <i class="fas fa-shopping-bag"></i> Continue Shopping
                </a>
                <a href="{% url 'logout' %}" class="btn-modern btn-danger-ghost">
                    <i class="fas fa-sign-out-alt"></i> Sign Out
                </a>
            </div>
        </div>

        <div class="profile-grid-layout">
            
            <!-- Tracking Column -->
            <div class="dashboard-col">
                <div class="block-header">
                    <h2 class="block-title">
                        <div class="title-icon"><i class="fas fa-box-open"></i></div>
                        Recent Orders
                    </h2>
                </div>

                {% if orders %}
                <div class="order-stream">
                    {% for o in orders %}
                    <div class="item-card">
                        <img src="{{ o.product_image|default:'https://via.placeholder.com/100' }}" class="item-preview" alt="Order">
                        <div class="item-content">
                            <span class="item-tag">{{ o.business_name }}</span>
                            <span class="item-name">{{ o.product_name }}</span>
                            <div class="item-meta">
                                <span class="status-pill {% if o.status == 'PENDING' %}status-pending{% elif o.status == 'COMPLETED' %}status-completed{% else %}status-cancelled{% endif %}">
                                    {{ o.status }}
                                </span>
                                <span><i class="far fa-calendar"></i> {{ o.created_at|slice:":10" }}</span>
                            </div>
                        </div>
                        <div class="item-price-tag">
                            {{ o.product_currency }} {{ o.offer_price|floatformat:0 }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty-canvas">
                    <div class="empty-icon-wrap"><i class="fas fa-shopping-cart"></i></div>
                    <p>No active orders found.</p>
                    <a href="{% url 'shop_home' %}" style="color: var(--accent-color); font-weight: 700; text-decoration: none;">Browse Store</a>
                </div>
                {% endif %}
            </div>

            <!-- Wishlist Column -->
            <div class="dashboard-col">
                <div class="block-header">
                    <h2 class="block-title">
                        <div class="title-icon"><i class="fas fa-heart"></i></div>
                        Your Wishlist
                    </h2>
                </div>

                {% if wishes %}
                <div class="wishlist-masonry">
                    {% for item in wishes %}
                    <a href="{% url 'product_detail' item.id %}" class="wish-brick">
                        <div class="brick-img-wrap">
                            <img src="{{ item.image_url|default:'https://via.placeholder.com/300' }}" class="brick-img" alt="Wishlist Item">
                        </div>
                        <div class="brick-body">
                            <div class="brick-name">{{ item.name }}</div>
                            <div class="brick-footer">
                                <div class="brick-price">{{ item.currency }} {{ item.price|floatformat:0 }}</div>
                                <div class="brick-icon"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty-canvas">
                    <div class="empty-icon-wrap"><i class="fas fa-heart"></i></div>
                    <p>Your wishlist is looking empty.</p>
                </div>
                {% endif %}
            </div>

        </div>

        <!-- Debugging Info -->
        <div class="debug-panel">
            UID: {{ debug_info.uid }} | OC: {{ debug_info.order_count }} | WC: {{ debug_info.wish_count }} | TF: {{ business.theme_component|yesno:"Y,N" }}
        </div>

    </div>

    {% include "storefront/partials/nexus_footer.html" %}

</body>
</html>"""

with open(r'c:\Users\user\nexus_web\storefront\templates\storefront\profile.html', 'w', encoding='utf-8') as f:
    f.write(profile_content)

print("Profile template fixed and synchronized.")
