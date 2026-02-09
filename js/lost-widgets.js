// Lost & Found Widgets Module
console.log('lost-widgets.js loaded');

// Render a single lost item card
function renderLostItem(item) {
    const imageUrl = item.image || item.imageUrl || '';
    const location = item.location || 'Location not specified';
    const date = item.date || item.dateAdded || 'Unknown date';
    const snippet = item.snippet || item.description || 'No description provided';
    const category = item.category || 'other';

    console.log(`Rendering item: ${item.title}, image URL:`, imageUrl);

    return `
        <div class="result-card" style="background: #0f0a1a; padding: 16px; margin-bottom: 16px; border-radius: 8px; border: 1px solid #2d1b4e; display: flex; gap: 16px;">
            ${imageUrl ? `
            <div style="flex-shrink: 0;">
                <img src="${imageUrl}" 
                     alt="${item.title}" 
                     style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px; background: #2d1b4e;" 
                     onload="console.log('Image loaded:', this.src)"
                     onerror="console.error('Image failed to load:', this.src); this.style.display='none'">
            </div>
            ` : `<div style="flex-shrink: 0; width: 120px; height: 120px; background: #2d1b4e; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666;">No image</div>`}
            <div style="flex: 1;">
                <div style="font-size: 0.75rem; color: #8b5cf6; margin-bottom: 4px; text-transform: uppercase;">
                    ${category} · ${date}
                </div>
                <h3 class="result-title" style="margin: 4px 0; font-size: 1.1rem; font-weight: 600;">
                    ${item.title}
                </h3>
                <p class="result-description" style="margin: 12px 0; font-size: 0.9rem; line-height: 1.5;">
                    ${snippet.substring(0, 150)}${snippet.length > 150 ? '...' : ''}
                </p>
                <div style="display: flex; gap: 16px; font-size: 0.85rem; color: #8b5cf6;">
                    <span>📍 ${location}</span>
                    <span>${item.contact || 'Contact provided'}</span>
                </div>
            </div>
        </div>
    `;
}

// Export for use in HTML
window.renderLostItem = renderLostItem;
