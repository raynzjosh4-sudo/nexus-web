// Community Widgets Module
console.log('community-widgets.js loaded');

// Render a single community post
function renderCommunityPost(post) {
    const imageUrl = post.image || post.image_url || '';
    const author = post.author || 'Anonymous';
    const date = post.date || post.created_at || 'Unknown date';
    const snippet = post.body || post.description || 'No description provided';
    const category = post.category || 'general';

    return `
        <div class="google-result" style="background: #0f0a1a; padding: 16px; margin-bottom: 16px; border-radius: 8px; border: 1px solid #2d1b4e; display: flex; gap: 16px; cursor: pointer;" onclick="window.location.href='detail.html?id=${post.id}'; return false;">
            <div style="flex: 1;">
                <div style="font-size: 0.85rem; color: #8b5cf6; margin-bottom: 4px; line-height: 1.2;">
                    Community · ${date}
                </div>
                <h3 class="result-title" style="margin: 4px 0; font-size: 1.25rem; font-weight: 500; color: #a855f7; line-height: 1.3;">
                    ${post.title}
                </h3>
                <p class="result-description" style="margin: 12px 0; font-size: 0.9rem; line-height: 1.6; color: #b0b0b0;">
                    ${snippet.substring(0, 200)}${snippet.length > 200 ? '...' : ''}
                </p>
                <div style="display: flex; gap: 24px; font-size: 0.85rem; color: #8b5cf6; padding-top: 8px;">
                    <span>👁️ ${post.views || 0} views</span>
                    <span>💬 ${post.replies || post.comments || 0} replies</span>
                    <span>${author}</span>
                </div>
            </div>
            ${imageUrl ? `
            <div style="flex-shrink: 0;">
                <img src="${imageUrl}" alt="${post.title}" style="width: 160px; height: 120px; object-fit: cover; border-radius: 8px; background: #2d1b4e;" onerror="this.style.display='none'">
            </div>
// Export for use in HTML  
window.renderCommunityPost = renderCommunityPost;
