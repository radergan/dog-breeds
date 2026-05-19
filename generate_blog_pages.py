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
        .blog-post-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .breadcrumbs {{
            margin-bottom: 30px;
            font-size: 14px;
            color: #666;
        }}
        
        .breadcrumbs a {{
            color: #5755d9;
            text-decoration: none;
        }}
        
        .breadcrumbs a:hover {{
            text-decoration: underline;
        }}
        
        .blog-post-header {{
            margin-bottom: 40px;
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

    <div class="blog-post-container">
        <div class="breadcrumbs">
            <a href="../index.html">Home</a> → <a href="../blog.html">Blog</a> → {post['title']}
        </div>
        
        <article class="blog-post">
            <div class="blog-post-header">
                {f'<div class="blog-post-category">{post["category"]}</div>' if post['category'] else ''}
                <h1 class="blog-post-title">{post['title']}</h1>
                <div class="blog-post-meta">
                    <span>📅 {post['published_date']}</span>
                    <span>✍️ {post['author']}</span>
                </div>
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
