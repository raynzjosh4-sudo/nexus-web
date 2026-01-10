import html
from django.template.loader import render_to_string

def render_component_list(components, context=None):
    """
    Renders a list of component dictionaries into a single HTML string.
    Using Django templates for Profile components.
    """
    if not components or not isinstance(components, list):
        return ""
    
    html_output = []
    for comp in components:
        if not isinstance(comp, dict): continue
        try:
            html_output.append(render_single_component(comp, context))
        except Exception as e:
            html_output.append(f"<!-- Render Error: {e} -->")
    
    return "\n".join(html_output)

def render_single_component(comp, context=None):
    # Use normalized type if available, else standard type
    c_type = comp.get('clean_type') or comp.get('type') or ''
    raw_type = c_type
    
    # Cleaning the type slightly more to be sure
    c_type = c_type.lower().replace('profile', '').replace('component', '')
        
    # Map cleaned type to template file
    template_map = {
        'hero': 'hero.html',
        'gallery': 'gallery.html',
        'video': 'video.html',
        'map': 'map.html',
        'heading': 'heading.html',
        'bio': 'bio.html',
        'contact': 'contact.html',
        'testimonial': 'testimonials.html', # Note plural s
        'testimonials': 'testimonials.html',
        'cta': 'cta.html',
        'calltoaction': 'cta.html',
        'pricing': 'pricing.html',
        'faq': 'faq.html',
        'featurelist': 'features.html', 
        'features': 'features.html',
        'team': 'team.html',
        'timeline': 'timeline.html',
        'filedownload': 'downloads.html',
        'downloads': 'downloads.html',
        'divider': 'divider.html',
        'portfolio': 'portfolio.html',
        'servicelist': 'services.html',
        'services': 'services.html',
        'booking': 'booking.html',
        'awards': 'awards.html',
        'tabbedcontent': 'tabs.html',
        'tabs': 'tabs.html',
        # 'feed': 'feed.html', # Missing
    }
    
    tpl_name = template_map.get(c_type)
    
    if tpl_name:
        # Pass full context (business, etc) plus the component
        ctx = {'component': comp}
        if context:
            ctx.update(context)
        
        try:
            return render_to_string(f'storefront/components/{tpl_name}', ctx)
        except Exception as e:
            return f"<!-- Template Error {tpl_name}: {e} -->"
    
    # Fallback for Legacy Types (Product Description components)
    return render_legacy_component(comp, raw_type)

def render_legacy_component(comp, c_type):
    content = ""
    c_type_orig = comp.get('type') # Use original type for legacy check
    
    # --- TEXT & HEADERS ---
    if c_type_orig == 'TextComponent':
        text = html.escape(comp.get('text', ''))
        style = comp.get('style', 'body')
        content = f'<div class="sc-comp text-component text-{style}">{text}</div>'
        
    elif c_type_orig == 'RichTextComponent':
        md_text = comp.get('markdownText', '')
        content = f'<div class="sc-comp richtext-component"><div class="richtext">{md_text}</div></div>'
        
    elif c_type_orig == 'ProductHeaderComponent':
        name = html.escape(comp.get('productName', ''))
        price = comp.get('price', 0)
        curr = comp.get('currency', '$')
        orig = comp.get('originalPrice', 0)
        
        orig_html = ''
        if orig and orig > price:
            orig_html = f'<span class="ph-original">{curr} {orig:,.0f}</span>'
            
        content = f'''
        <div class="sc-comp header-component">
            <h2 class="ph-title">{name}</h2>
            <div class="ph-pricing">
                <span class="ph-price">{curr} {price:,.0f}</span>
                {orig_html}
            </div>
        </div>'''

    # --- LISTS & TABLES ---
    elif c_type_orig == 'BulletedListComponent':
        items = comp.get('items', [])
        style = comp.get('listStyle', 'bullet')
        title = comp.get('title')
        title_html = f'<h4 class="list-title">{html.escape(title)}</h4>' if title else ''
        
        list_items = ""
        for item in items:
            list_items += f'<li><span class="item-content">{html.escape(str(item))}</span></li>'
            
        style_map = {'bullet': 'bullet', 'numbered': 'numbered', 'checkmark': 'checkmark', 'icon': 'checkmark'}
        css_style = style_map.get(style, 'bullet')
        tag = "ol" if style == 'numbered' else "ul"
        
        content = f'''
        <div class="sc-comp bulleted-list-component">
            {title_html}
            <div class="list-container">
                <{tag} class="styled-list {css_style}">
                    {list_items}
                </{tag}>
            </div>
        </div>'''
        
    elif c_type_orig == 'SpecTableComponent':
        title = comp.get('title')
        title_html = f'<h3 class="spec-header">{html.escape(title)}</h3>' if title else ''
        specs = comp.get('specs', {})
        rows = ""
        for k,v in specs.items():
            rows += f'<tr><td class="spec-key">{html.escape(k)}</td><td class="spec-val">{html.escape(str(v))}</td></tr>'
            
        content = f'''
        <div class="sc-comp spec-component">
            {title_html}
            <div class="spec-table-wrapper">
                <table class="spec-table"><tbody>{rows}</tbody></table>
            </div>
        </div>'''
        
    # --- MEDIA ---
    elif c_type_orig == 'ImageComponent':
        url = comp.get('imageUrl') or comp.get('image_url')
        if not url: return ""
        caption = html.escape(comp.get('caption', ''))
        cap_html = f'<h4 class="image-caption">{caption}</h4>' if caption else ''
        content = f'''
        <div class="sc-comp image-component">
            {cap_html}
            <div class="image-wrap">
                <img src="{url}" alt="{caption}" loading="lazy">
            </div>
        </div>'''
        
    elif c_type_orig == 'VideoComponent':
        videos = comp.get('videos', [])
        if videos and isinstance(videos, list):
            v_url = videos[0].get('videoUrl')
            if v_url:
                content = f'''
                <div class="sc-comp video-component">
                    <video controls class="comp-video">
                        <source src="{v_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>'''

    elif c_type_orig == 'AudioComponent':
        a_url = comp.get('audioUrl')
        title = html.escape(comp.get('title', ''))
        if a_url:
            content = f'''
            <div class="sc-comp audio-component">
                <div class="audio-header"><i class="fas fa-music"></i> <span>{title}</span></div>
                <audio controls class="comp-audio">
                    <source src="{a_url}" type="audio/mpeg">
                </audio>
            </div>'''

    elif c_type_orig == 'MapLocationComponent':
        lat = comp.get('latitude')
        lng = comp.get('longitude')
        addr = html.escape(comp.get('address', 'View on Map'))
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        content = f'''
        <div class="sc-comp map-component">
            <a href="{map_link}" target="_blank" class="map-card-link">
                <div class="map-icon"><i class="fas fa-map-marker-alt"></i></div>
                <div class="map-info">
                    <span class="map-label">Location</span>
                    <span class="map-address">{addr}</span>
                </div>
                <div class="map-arrow"><i class="fas fa-external-link-alt"></i></div>
            </a>
        </div>'''

    # --- ACTIONS ---
    elif c_type_orig == 'ContactComponent':
        label = html.escape(comp.get('label') or 'Contact Us')
        phone = comp.get('phone')
        whatsapp = comp.get('whatsapp')
        email = comp.get('email')
        
        actions = []
        if phone: 
            actions.append(f'<a href="tel:{phone}" class="contact-btn phone"><i class="fas fa-phone"></i> Call</a>')
        if whatsapp:
            actions.append(f'<a href="https://wa.me/{whatsapp}" class="contact-btn whatsapp"><i class="fab fa-whatsapp"></i> WhatsApp</a>')
        if email:
            actions.append(f'<a href="mailto:{email}" class="contact-btn email"><i class="fas fa-envelope"></i> Email</a>')
            
        actions_html = "".join(actions)
        if actions_html:
            content = f'''
            <div class="sc-comp contact-component">
                <h4 class="contact-title">{label}</h4>
                <div class="contact-grid">{actions_html}</div>
            </div>'''

    elif c_type_orig == 'CallToActionComponent':
        text = html.escape(comp.get('buttonText', 'Action'))
        actionType = comp.get('actionType')
        url = comp.get('actionValue')
        
        if actionType == 'viewWebsite' and url:
            content = f'<div class="sc-comp cta-component"><a href="{url}" target="_blank" class="btn-cta">{text}</a></div>'
        else:
            content = f'<div class="sc-comp cta-component"><button class="btn-cta">{text}</button></div>'

    elif c_type_orig == 'DividerComponent':
        content = '<div class="sc-comp divider-component"><hr class="comp-divider"></div>'

    # --- LAYOUT ---
    elif c_type_orig == 'CardComponent':
        children = comp.get('children', [])
        inner = render_component_list(children)
        content = f'''
        <div class="sc-comp card-component">
            {inner}
        </div>'''

    elif c_type_orig == 'ColumnComponent':
        children = comp.get('children', [])
        inner = render_component_list(children)
        content = f'''
        <div class="sc-comp column-component">
            {inner}
        </div>'''

    elif c_type_orig == 'RowComponent':
        children = comp.get('children', [])
        inner = render_component_list(children)
        content = f'''
        <div class="sc-comp row-component">
            {inner}
        </div>'''
        
    elif c_type_orig == 'ExpandableComponent':
        title = html.escape(comp.get('title', 'More Info'))
        children = comp.get('children', [])
        inner = render_component_list(children)
        content = f'''
        <div class="sc-comp expandable-component">
            <details class="comp-details">
                <summary class="comp-summary">{title}</summary>
                <div class="comp-details-content">{inner}</div>
            </details>
        </div>'''

    elif c_type_orig == 'BookingComponent':
        name = html.escape(comp.get('serviceName', 'Service'))
        desc = html.escape(comp.get('serviceDescription', ''))
        price = comp.get('startingPrice')
        url = comp.get('bookingUrl')
        img = comp.get('imageUrl')
        
        img_html = f'<img src="{img}" class="booking-img">' if img else ''
        price_html = f'<div class="booking-price">Starts at {price}</div>' if price else ''
        url_html = f'<a href="{url}" target="_blank" class="btn-booking">Book Now</a>' if url else ''
        
        content = f'''
        <div class="sc-comp booking-component">
            {img_html}
            <div class="booking-details">
                <h4 class="booking-name">{name}</h4>
                <p class="booking-desc">{desc}</p>
                {price_html}
                {url_html}
            </div>
        </div>'''

    elif c_type_orig == 'CommentsComponent':
        comments = comp.get('comments', [])
        comment_items = ""
        for c in comments:
            user = html.escape(c.get('userName', 'User'))
            text = html.escape(c.get('commentText', ''))
            avatar = c.get('userAvatarUrl') or 'https://via.placeholder.com/40/333/fff?text=U'
            comment_items += f'''
            <div class="comment-item">
                <img src="{avatar}" class="comment-avatar">
                <div class="comment-body">
                    <span class="comment-user">{user}</span>
                    <p class="comment-text">{text}</p>
                </div>
            </div>'''
            
        content = f'''
        <div class="sc-comp comments-component">
            <h4 class="comps-title">Comments</h4>
            <div class="comments-list">{comment_items}</div>
        </div>'''

    if content:
        return f'<div class="sc-comp-wrapper">{content}</div>'
    return ""
