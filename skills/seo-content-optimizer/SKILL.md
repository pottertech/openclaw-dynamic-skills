---
name: seo-content-optimizer
description: SEO optimization for websites and blog posts. Use when optimizing content for search engines, improving meta tags, generating schema markup, analyzing keywords, or improving search rankings.
---

# SEO Content Optimizer

Comprehensive SEO optimization for websites, blog posts, and web content.

## When to Use

- Optimizing blog posts for search engines
- Improving meta tags (title, description)
- Generating schema markup
- Keyword research and optimization
- Analyzing on-page SEO factors
- Improving internal linking
- Creating XML sitemaps
- Fixing SEO issues
- Competitor SEO analysis

## On-Page SEO

### Title Tag Optimization

**Best Practices:**
- ✅ 50-60 characters (display limit)
- ✅ Include primary keyword near start
- ✅ Add brand name at end
- ✅ Make it compelling (CTR matters)

**Examples:**
```
❌ "Blog Post About AI"
✅ "AI Agents in 2026: Complete Guide | Plot Twist Daily"

❌ "How to Code Better"
✅ "10 Coding Best Practices Every Developer Needs | Plot Twist"
```

**For Hugo:**
```yaml
# In frontmatter
title: "AI Agents in 2026: Complete Guide"
```

### Meta Description

**Best Practices:**
- ✅ 150-160 characters
- ✅ Include primary keyword
- ✅ Add call-to-action
- ✅ Summarize content value

**Examples:**
```
❌ "This is a post about AI agents."
✅ "Learn how AI agents are transforming software development in 2026. Complete guide with examples, tools, and best practices. Read now!"
```

**For Hugo:**
```yaml
# In frontmatter
description: "Learn how AI agents are transforming software development in 2026. Complete guide with examples, tools, and best practices."
```

### Header Structure

**Proper Hierarchy:**
```markdown
# H1: Main Title (one per page)
## H2: Major Sections
### H3: Subsections
#### H4: Details (if needed)
```

**Example:**
```markdown
# AI Agents in 2026: Complete Guide

## What Are AI Agents?
### Definition
### Key Characteristics

## How AI Agents Work
### Architecture Overview
### Tool Integration

## Use Cases
### Software Development
### Customer Service
### Data Analysis

## Getting Started
### Tools You Need
### First Steps
```

## Keyword Optimization

### Keyword Research

```python
def analyze_keyword_difficulty(keyword):
    """Analyze keyword difficulty (simplified)"""
    
    # Check search volume (use API in production)
    search_volume = get_search_volume(keyword)
    
    # Check competition
    competition = get_competition_level(keyword)
    
    # Calculate difficulty score
    if search_volume > 10000 and competition == 'high':
        return 'hard'
    elif search_volume > 1000 and competition == 'medium':
        return 'medium'
    else:
        return 'easy'

# Usage
difficulty = analyze_keyword_difficulty('AI agents tutorial')
print(f"Keyword difficulty: {difficulty}")
```

### Keyword Placement

**Optimal Placement:**
1. ✅ Title tag (most important)
2. ✅ Meta description
3. ✅ H1 heading
4. ✅ First 100 words
5. ✅ H2/H3 subheadings
6. ✅ Throughout content (natural density 1-2%)
7. ✅ Image alt text
8. ✅ URL slug

**Example:**
```markdown
---
title: "AI Agents Tutorial: Complete Guide for 2026"
description: "Learn how to build AI agents with this complete tutorial. Step-by-step guide with code examples and best practices."
---

# AI Agents Tutorial: Complete Guide for 2026

AI agents are transforming how we build software. In this comprehensive **AI agents tutorial**, you'll learn everything you need to know...

## What Are AI Agents?

AI agents are autonomous programs that can...

## How to Build AI Agents

Building AI agents requires understanding of...
```

## Schema Markup

### Article Schema (for Blog Posts)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "AI Agents in 2026: Complete Guide",
  "description": "Learn how AI agents are transforming software development",
  "image": "https://plottwistdaily.com/images/ai-agents.jpg",
  "author": {
    "@type": "Person",
    "name": "Arty Craftson",
    "url": "https://plottwistdaily.com/author/arty"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Plot Twist Daily",
    "logo": {
      "@type": "ImageObject",
      "url": "https://plottwistdaily.com/logo.png"
    }
  },
  "datePublished": "2026-03-05",
  "dateModified": "2026-03-05"
}
```

**For Hugo:**
```yaml
# In frontmatter
schema:
  type: Article
  author: Arty Craftson
  publisher: Plot Twist Daily
```

### FAQ Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What are AI agents?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI agents are autonomous programs that can perceive their environment and take actions to achieve goals."
      }
    },
    {
      "@type": "Question",
      "name": "How do AI agents work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI agents use sensors to perceive their environment, process information using AI models, and take actions through actuators."
      }
    }
  ]
}
```

## Internal Linking

### Best Practices

- ✅ Link to related content
- ✅ Use descriptive anchor text
- ✅ Link deep (not just homepage)
- ✅ Maintain logical site structure
- ✅ Update old posts with new links

**Example:**
```markdown
## Related Posts

- [Building Your First AI Agent](/building-ai-agent)
- [AI Agent Tools Comparison](/ai-tools-comparison)
- [Advanced AI Agent Patterns](/advanced-ai-patterns)
```

### Automated Internal Linking

```python
def suggest_internal_links(current_post, all_posts):
    """Suggest relevant internal links"""
    
    # Extract keywords from current post
    keywords = extract_keywords(current_post['content'])
    
    # Find matching posts
    suggestions = []
    for post in all_posts:
        if post['url'] == current_post['url']:
            continue
        
        score = calculate_relevance(keywords, post['keywords'])
        if score > 0.5:
            suggestions.append({
                'url': post['url'],
                'title': post['title'],
                'relevance': score
            })
    
    # Return top 3
    return sorted(suggestions, key=lambda x: x['relevance'], reverse=True)[:3]
```

## Image Optimization

### Alt Text

**Best Practices:**
- ✅ Be descriptive and specific
- ✅ Include keyword if natural
- ✅ Keep it concise (under 125 chars)
- ✅ Don't stuff keywords

**Examples:**
```
❌ "image1.jpg"
✅ "ferrari-sf26-formula-1-car.jpg"

❌ alt="car"
✅ alt="Red Ferrari SF-26 Formula 1 racing car on track"
```

### Image Compression

```bash
# Compress images for web
convert input.jpg -quality 85 -resize 1200x output.jpg

# Create WebP version
cwebp -q 80 input.jpg -o output.webp
```

## Technical SEO

### XML Sitemap

**For Hugo:**
```yaml
# config.toml
[outputs]
  home = ["HTML", "RSS", "sitemap"]

[sitemap]
  changefreq = "weekly"
  filename = "sitemap.xml"
  priority = 0.5
```

### robots.txt

```txt
User-agent: *
Allow: /

# Disallow admin areas
Disallow: /admin/
Disallow: /wp-admin/

# Sitemap location
Sitemap: https://plottwistdaily.com/sitemap.xml
```

### Page Speed

**Optimization Tips:**
- ✅ Compress images (WebP format)
- ✅ Minify CSS/JS
- ✅ Enable browser caching
- ✅ Use CDN
- ✅ Lazy load images
- ✅ Reduce server response time

## SEO Audit Checklist

### Pre-Publish

- [ ] Title tag optimized (50-60 chars)
- [ ] Meta description compelling (150-160 chars)
- [ ] Primary keyword in title
- [ ] Primary keyword in first 100 words
- [ ] Proper header hierarchy (H1 → H2 → H3)
- [ ] Internal links to related content
- [ ] Image alt text descriptive
- [ ] Schema markup added
- [ ] URL slug clean and descriptive
- [ ] Mobile-friendly layout

### Post-Publish

- [ ] Submit to Google Search Console
- [ ] Check indexing status
- [ ] Monitor rankings for target keywords
- [ ] Track organic traffic
- [ ] Update internal links from old posts
- [ ] Share on social media
- [ ] Monitor for broken links

## Tools

### Free Tools

- **Google Search Console** - Indexing, rankings, errors
- **Google Analytics** - Traffic analysis
- **Google Keyword Planner** - Keyword research
- **Screaming Frog** (free version) - Site audit
- **PageSpeed Insights** - Performance analysis

### Paid Tools

- **Ahrefs** - Backlink analysis, keyword research
- **SEMrush** - Competitor analysis, rank tracking
- **Moz Pro** - SEO audit, rank tracking
- **Surfer SEO** - Content optimization

## Hugo Integration

### SEO Partial Template

```html
<!-- layouts/partials/seo.html -->
<title>{{ .Title }} | {{ .Site.Title }}</title>
<meta name="description" content="{{ .Params.description }}">
<meta name="keywords" content="{{ delimit .Params.tags ", " }}">

<!-- Open Graph -->
<meta property="og:title" content="{{ .Title }}">
<meta property="og:description" content="{{ .Params.description }}">
<meta property="og:image" content="{{ .Params.image }}">
<meta property="og:url" content="{{ .Permalink }}">

<!-- Schema.org -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ .Title }}",
  "description": "{{ .Params.description }}",
  "author": {
    "@type": "Person",
    "name": "{{ .Params.author }}"
  }
}
</script>
```

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
