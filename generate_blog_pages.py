"""Generate static blog pages from database"""
import sqlite3
import os
import json

def export_blog_posts_js():
    """Export blog posts to blog-posts.js for listing page"""
    conn = sqlite3.connect('dog_breeds.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM blog_posts WHERE is_published = 1 ORDER BY published_date DESC')
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Convert to JavaScript format
    js_posts = []
    for post in posts:
        js_post = {
            'id': post['id'],
            'slug': post['slug'],
            'title': post['title'],
            'excerpt': post['excerpt'],
            'featuredImage': post['featured_image'],
            'publishedDate': post['published_date'],
            'category': post['category'],
            'tags': post['tags'].split(',') if post.get('tags') else []
        }
        js_posts.append(js_post)
    
    # Write to blog-posts.js
    js_content = f"const blogPosts = {json.dumps(js_posts, indent=2)};\n"
    
    with open('blog-posts.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Exported {len(js_posts)} blog posts to blog-posts.js")
    return posts

def generate_blog_post_page(post):
    """Generate individual blog post HTML page"""
    
    # HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} - Dog Breed Finder Blog</title>
    <meta name="description" content="{post['excerpt'] or post['title']}">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre.min.css">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre-exp.min.css">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre-icons.min.css">
    <link rel="stylesheet" href="../styles.css">
    <style>
        .blog-post-content-wrapper {{
            background: #ffffff;
            border-radius: 7px;
            padding: 40px;
            border: 1px solid #d0d0d0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        .blog-post-header {{
            flex: 1;
        }}
        
        .blog-post-category {{
            display: inline-block;
            background: #5755d9;
            color: white;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 16px;
        }}
        
        .blog-post-title {{
            font-size: 42px;
            font-weight: bold;
            color: #302f79;
            line-height: 1.2;
            margin-bottom: 16px;
        }}
        
        .blog-post-meta {{
            display: flex;
            gap: 20px;
            color: #888;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        
        .blog-post-image {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 40px;
        }}
        
        .blog-post-content {{
            font-size: 18px;
            line-height: 1.8;
            color: #333;
        }}
        
        .blog-post-content h2 {{
            font-size: 32px;
            color: #302f79;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        
        .blog-post-content h3 {{
            font-size: 24px;
            color: #302f79;
            margin-top: 30px;
            margin-bottom: 16px;
        }}
        
        .blog-post-content p {{
            margin-bottom: 20px;
        }}
        
        .blog-post-content ul, .blog-post-content ol {{
            margin-bottom: 20px;
            padding-left: 30px;
        }}
        
        .blog-post-content li {{
            margin-bottom: 10px;
        }}
        
        .blog-post-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 30px 0;
        }}
        
        .blog-post-content a {{
            color: #5755d9;
            text-decoration: none;
        }}
        
        .blog-post-content a:hover {{
            text-decoration: underline;
        }}
        
        .blog-post-content blockquote {{
            border-left: 4px solid #5755d9;
            padding-left: 20px;
            margin: 30px 0;
            font-style: italic;
            color: #666;
        }}
        
        .blog-post-content code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 16px;
        }}
        
        .blog-post-content pre {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 30px 0;
        }}
        
        .blog-post-content pre code {{
            background: none;
            padding: 0;
        }}
        
        .blog-post-tags {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid #eee;
        }}
        
        .blog-post-tags h4 {{
            font-size: 14px;
            color: #888;
            margin-bottom: 12px;
            font-weight: normal;
        }}
        
        .tag {{
            display: inline-block;
            background: #f0f0f0;
            color: #666;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 13px;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        
        .back-to-blog {{
            display: inline-block;
            margin-top: 40px;
            color: #5755d9;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .back-to-blog:hover {{
            text-decoration: underline;
        }}
        
        .blog-header-wrapper {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 40px;
        }}
        
        .edit-blog-btn {{
            flex-shrink: 0;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <div class="header-left">
                <a href="../index.html" class="logo">woof_db</a>
                <div class="tagline">&nbsp Find Your Perfect Dog Breed</div>
            </div>
        </div>
    </header>

    <nav class="top-nav">
        <div class="top-nav-container">
            <div class="stats-bar">
                <div class="stat-item">
                    <a href="../index.html" style="color: inherit; text-decoration: none;">Home</a>
                </div>
                <div class="stat-item">
                    <a href="../blog.html" style="color: inherit; text-decoration: none; font-weight: bold;">Blog</a>
                </div>
                <div class="stat-item">
                    <span>About Us</span>
                </div>
            </div>
        </div>
    </nav>

    <div class="main-layout">
        <aside class="sidebar">
            <div class="side-nav">
                <div class="accordion">
                    <input type="checkbox" id="accordion-0" name="accordion-checkbox" checked>
                    <label class="accordion-header" for="accordion-0">Recent Posts</label>
                    <div class="accordion-body">
                        <div id="recent-posts-sidebar">
                            <p style="color: #888; font-size: 13px; padding: 8px 0;">Loading...</p>
                        </div>
                    </div>
                </div>
                
                <div class="accordion">
                    <input type="checkbox" id="accordion-1" name="accordion-checkbox" checked>
                    <label class="accordion-header" for="accordion-1">Categories</label>
                    <div class="accordion-body">
                        <div id="categories-sidebar">
                            <p style="color: #888; font-size: 13px; padding: 8px 0;">Loading...</p>
                        </div>
                    </div>
                </div>

                <div class="accordion">
                    <input type="checkbox" id="accordion-2" name="accordion-checkbox" checked>
                    <label class="accordion-header" for="accordion-2">Popular Tags</label>
                    <div class="accordion-body">
                        <div id="tags-sidebar" style="display: flex; flex-wrap: wrap; gap: 8px;">
                            <p style="color: #888; font-size: 13px; padding: 8px 0;">Loading...</p>
                        </div>
                    </div>
                </div>
            </div>
        </aside>

        <main class="main-content">
            <div class="breadcrumb-search-container">
                <ul class="breadcrumb">
                    <li class="breadcrumb-item">
                        <a href="../index.html">Home</a>
                    </li>
                    <li class="breadcrumb-item">
                        <a href="../blog.html">Blog</a>
                    </li>
                    <li class="breadcrumb-item">
                        <a href="#">{post['title']}</a>
                    </li>
                </ul>
            </div>
            
            <div class="blog-post-content-wrapper">
        
        <article class="blog-post">
            <div class="blog-header-wrapper">
                <div class="blog-post-header">
                    {f'<div class="blog-post-category">{post["category"]}</div>' if post['category'] else ''}
                    <h1 class="blog-post-title">{post['title']}</h1>
                    <div class="blog-post-meta">
                        <span>📅 {post['published_date']}</span>
                        <span>✍️ {post['author']}</span>
                    </div>
                </div>
                <a href="http://localhost:5000/blog/{post['id']}/edit" target="_blank" class="btn btn-primary btn-sm edit-blog-btn" title="Edit blog post">
                    <i class="icon icon-edit"></i> Edit
                </a>
            </div>
            
            {f'<img src="{post["featured_image"]}" alt="{post["title"]}" class="blog-post-image">' if post['featured_image'] else ''}
            
            <div class="blog-post-content">
                {post['content']}
            </div>
            
            {f'''<div class="blog-post-tags">
                <h4>Tags:</h4>
                {' '.join([f'<span class="tag">{tag.strip()}</span>' for tag in post['tags'].split(',')])}
            </div>''' if post['tags'] else ''}
        </article>
        
        <a href="../blog.html" class="back-to-blog">← Back to Blog</a>
            </div>
        </main>
    </div>
    
    <script src="../blog-posts.js"></script>
    <script>
        // Populate sidebar
        if (typeof blogPosts !== 'undefined') {{
            // Recent Posts
            const recentPostsContainer = document.getElementById('recent-posts-sidebar');
            if (blogPosts.length > 0) {{
                const recentPosts = blogPosts.slice(0, 5);
                recentPostsContainer.innerHTML = recentPosts.map(post => `
                    <div class="subfamily-item" style="cursor: pointer; padding-left: 12px;" onclick="window.location.href='${{post.slug}}.html'">
                        <div class="subfamily-name" style="font-size: 14px; color: #302f79;">${{post.title}}</div>
                        <div class="subfamily-desc" style="font-size: 12px;">${{post.publishedDate}}</div>
                    </div>
                `).join('');
            }}
            
            // Categories
            const categoriesContainer = document.getElementById('categories-sidebar');
            const categoryCount = {{}};
            blogPosts.forEach(post => {{
                if (post.category) {{
                    categoryCount[post.category] = (categoryCount[post.category] || 0) + 1;
                }}
            }});
            
            if (Object.keys(categoryCount).length > 0) {{
                categoriesContainer.innerHTML = Object.entries(categoryCount)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([category, count]) => `
                        <div class="subfamily-item" style="cursor: pointer; padding-left: 12px;" onclick="window.location.href='../blog.html'">
                            <div class="subfamily-name">${{category}}</div>
                            <div class="subfamily-desc">${{count}} post${{count !== 1 ? 's' : ''}}</div>
                        </div>
                    `).join('');
            }}
            
            // Tags
            const tagsContainer = document.getElementById('tags-sidebar');
            const allTags = new Set();
            blogPosts.forEach(post => {{
                if (post.tags && Array.isArray(post.tags)) {{
                    post.tags.forEach(tag => allTags.add(tag.trim()));
                }}
            }});
            
            if (allTags.size > 0) {{
                tagsContainer.innerHTML = Array.from(allTags)
                    .sort()
                    .map(tag => `
                        <span class="chip" style="font-size: 11px; padding: 4px 10px; cursor: pointer;" onclick="window.location.href='../blog.html'">${{tag}}</span>
                    `).join('');
            }}
        }}
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Generate all blog pages"""
    # Export blog posts to JS file
    posts = export_blog_posts_js()
    
    # Create blog directory
    os.makedirs('blog', exist_ok=True)
    
    # Generate individual post pages
    for post in posts:
        html = generate_blog_post_page(post)
        filepath = os.path.join('blog', f"{post['slug']}.html")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated blog/{post['slug']}.html")
    
    print(f"\nBlog generation complete!")
    print(f"- {len(posts)} blog posts generated")
    print(f"- blog-posts.js exported")

if __name__ == '__main__':
    main()
