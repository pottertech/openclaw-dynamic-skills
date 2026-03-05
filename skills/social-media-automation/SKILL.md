---
name: social-media-automation
description: Automate social media posting across Twitter/X, Instagram, LinkedIn, and other platforms. Use when scheduling posts, creating threads, cross-posting content, or managing social media presence.
---

# Social Media Automation

Automated social media posting, scheduling, and management across multiple platforms.

## When to Use

- Posting to Twitter/X (threads, replies, scheduling)
- Instagram post/reel publishing
- LinkedIn article posting
- Cross-platform content distribution
- Scheduling posts in advance
- Hashtag optimization
- Engagement tracking
- Content calendar management

## Platform Integrations

### Twitter/X (via OpenTweet API)

**Setup:**
```bash
# Get API key from https://opentweet.io
export OPENTWEET_API_KEY="your_api_key"
```

**Post Tweet:**
```bash
curl -X POST https://api.opentweet.io/v1/tweets \
  -H "Authorization: Bearer $OPENTWEET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Just launched our new product! 🚀\n\nCheck it out: https://example.com",
    "schedule_at": "2026-03-06T09:00:00Z"
  }'
```

**Create Thread:**
```bash
curl -X POST https://api.opentweet.io/v1/threads \
  -H "Authorization: Bearer $OPENTWEET_API_KEY" \
  -d '{
    "tweets": [
      "1/5 Let me share what I learned about AI agents...",
      "2/5 First, understand the core architecture...",
      "3/5 Second, focus on reliable tool integration...",
      "4/5 Third, implement proper error handling...",
      "5/5 Finally, always test in production-like environments."
    ],
    "schedule_at": "2026-03-06T10:00:00Z"
  }'
```

**Schedule Multiple Posts:**
```python
import requests
from datetime import datetime, timedelta

API_KEY = "your_opentweet_api_key"
BASE_URL = "https://api.opentweet.io/v1"

posts = [
    "Good morning! Starting the day with some coding ☕💻",
    "Just shipped a new feature! Check it out: https://example.com",
    "Hot take: AI agents will change software development forever",
    "Working late tonight. The grind never stops! 🌙",
]

for i, text in enumerate(posts):
    schedule_time = datetime.now() + timedelta(hours=i*3)
    
    response = requests.post(
        f"{BASE_URL}/tweets",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "text": text,
            "schedule_at": schedule_time.isoformat() + "Z"
        }
    )
    
    print(f"Scheduled post {i+1}: {response.status_code}")
```

### Instagram (via Graph API)

**Setup:**
```bash
# Need Facebook App + Instagram Business Account
export INSTAGRAM_ACCESS_TOKEN="your_token"
export INSTAGRAM_BUSINESS_ID="your_business_id"
```

**Post Image:**
```bash
# 1. Create media container
curl -X POST "https://graph.facebook.com/v18.0/{ig-user-id}/media" \
  -d "image_url=https://example.com/image.jpg" \
  -d "caption=Amazing sunset! 🌅 #photography #nature" \
  -d "access_token=$INSTAGRAM_ACCESS_TOKEN"

# 2. Publish media
curl -X POST "https://graph.facebook.com/v18.0/{ig-user-id}/media_publish" \
  -d "creation_id={media-container-id}" \
  -d "access_token=$INSTAGRAM_ACCESS_TOKEN"
```

**Post Reel:**
```bash
curl -X POST "https://graph.facebook.com/v18.0/{ig-user-id}/media" \
  -d "video_url=https://example.com/reel.mp4" \
  -d "media_type=REELS" \
  -d "caption=New reel! 🎬 #reels #video" \
  -d "access_token=$INSTAGRAM_ACCESS_TOKEN"
```

### LinkedIn (via LinkedIn API)

**Setup:**
```bash
export LINKEDIN_ACCESS_TOKEN="your_token"
export LINKEDIN_PERSON_URN="urn:li:person:YOUR_ID"
```

**Post Article:**
```bash
curl -X POST "https://api.linkedin.com/v2/ugcPosts" \
  -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  -d '{
    "author": "'$LINKEDIN_PERSON_URN'",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": {
          "text": "Excited to announce our new product launch! 🚀\n\nAfter months of hard work, we'\''re finally ready to share this with the world.\n\n#innovation #startup #technology"
        },
        "shareMediaCategory": "NONE"
      }
    },
    "visibility": {
      "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
  }'
```

## Content Workflows

### 1. Cross-Post Blog to All Platforms

```python
#!/usr/bin/env python3

import requests
from datetime import datetime

# Blog post content
blog_title = "How AI Agents Are Changing Development"
blog_url = "https://plottwistdaily.com/ai-agents-development"
blog_summary = "AI agents are transforming how we build software. Here'\''s what you need to know."

# Twitter thread
twitter_thread = [
    f"🧵 New blog post: {blog_title}",
    f"{blog_summary}",
    f"Key takeaways:\n- AI agents automate repetitive tasks\n- Focus on high-level architecture\n- Faster iteration cycles\n- Better code quality",
    f"Read the full post: {blog_url}"
]

# LinkedIn post
linkedin_post = f"""
{blog_title}

{blog_summary}

In this post, I explore:
• The rise of AI-powered development tools
• How agents are changing workflows
• What this means for developers
• Future trends to watch

Read more: {blog_url}

#AI #SoftwareDevelopment #Innovation #Technology
"""

# Schedule posts
schedule_twitter_thread(twitter_thread, datetime.now())
schedule_linkedin_post(linkedin_post, datetime.now() + timedelta(minutes=30))
```

### 2. Generate Hashtags

```python
def generate_hashtags(topic, platform='twitter'):
    """Generate optimized hashtags for topic"""
    
    hashtag_sets = {
        'ai': ['#AI', '#MachineLearning', '#DeepLearning', '#ArtificialIntelligence', '#Tech'],
        'coding': ['#coding', '#programming', '#developer', '#softwareengineering', '#code'],
        'startup': ['#startup', '#entrepreneur', '#business', '#innovation', '#founder'],
        'design': ['#design', '#ux', '#ui', '#graphicdesign', '#creative'],
    }
    
    base_tags = hashtag_sets.get(topic, ['#tech'])
    
    if platform == 'instagram':
        # Instagram: 10-15 hashtags
        return ' '.join(base_tags + [f'#{topic}'] * 5)
    elif platform == 'twitter':
        # Twitter: 2-3 hashtags max
        return ' '.join(base_tags[:3])
    elif platform == 'linkedin':
        # LinkedIn: 3-5 professional hashtags
        return ' '.join(base_tags[:5])
    
    return ' '.join(base_tags)

# Usage
hashtags = generate_hashtags('ai', 'twitter')
# Output: #AI #MachineLearning #DeepLearning
```

### 3. Content Calendar

```python
import json
from datetime import datetime, timedelta

class ContentCalendar:
    def __init__(self):
        self.posts = []
    
    def add_post(self, platform, content, scheduled_time):
        self.posts.append({
            'platform': platform,
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'status': 'scheduled'
        })
    
    def save(self, filename='content_calendar.json'):
        with open(filename, 'w') as f:
            json.dump(self.posts, f, indent=2)
    
    def load(self, filename='content_calendar.json'):
        with open(filename, 'r') as f:
            self.posts = json.load(f)
    
    def get_upcoming(self, hours=24):
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        return [
            post for post in self.posts
            if now <= datetime.fromisoformat(post['scheduled_time']) <= cutoff
        ]

# Usage
calendar = ContentCalendar()
calendar.add_post(
    platform='twitter',
    content="Good morning! Starting the day with some coding ☕",
    scheduled_time=datetime.now() + timedelta(hours=1)
)
calendar.save()
```

### 4. Auto-Post from RSS Feed

```python
import feedparser
import requests

def check_and_post_new_articles(rss_url, posted_urls_file='posted_urls.txt'):
    """Check RSS feed and post new articles"""
    
    # Load already posted URLs
    try:
        with open(posted_urls_file, 'r') as f:
            posted_urls = set(f.read().splitlines())
    except FileNotFoundError:
        posted_urls = set()
    
    # Parse RSS feed
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries[:3]:  # Last 3 articles
        if entry.link not in posted_urls:
            # Create tweet
            tweet = f"New article: {entry.title}\n\n{entry.link}"
            
            # Post to Twitter
            post_to_twitter(tweet)
            
            # Mark as posted
            posted_urls.add(entry.link)
            with open(posted_urls_file, 'w') as f:
                f.write('\n'.join(posted_urls))
            
            print(f"Posted: {entry.title}")

# Usage (run via cron every hour)
check_and_post_new_articles('https://plottwistdaily.com/rss')
```

## Engagement Tracking

### Twitter Analytics

```python
def get_tweet_analytics(tweet_id):
    """Get engagement metrics for tweet"""
    
    response = requests.get(
        f"https://api.opentweet.io/v1/tweets/{tweet_id}/analytics",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    data = response.json()
    return {
        'impressions': data.get('impressions', 0),
        'likes': data.get('likes', 0),
        'retweets': data.get('retweets', 0),
        'replies': data.get('replies', 0),
        'clicks': data.get('link_clicks', 0)
    }

# Usage
metrics = get_tweet_analytics('tweet_id_123')
print(f"Impressions: {metrics['impressions']}")
print(f"Engagement rate: {(metrics['likes'] + metrics['retweets']) / metrics['impressions'] * 100:.2f}%")
```

## Best Practices

### Twitter/X
- ✅ Post 3-5 times per day
- ✅ Use 2-3 hashtags max
- ✅ Include visuals when possible
- ✅ Engage with replies promptly
- ✅ Post threads for longer content
- ⏰ Best times: 9 AM, 12 PM, 6 PM

### Instagram
- ✅ Post 1-2 times per day
- ✅ Use 10-15 relevant hashtags
- ✅ High-quality visuals essential
- ✅ Stories for behind-the-scenes
- ✅ Reels for maximum reach
- ⏰ Best times: 11 AM, 7 PM

### LinkedIn
- ✅ Post 1 time per day (weekdays)
- ✅ Use 3-5 professional hashtags
- ✅ Long-form content performs well
- ✅ Include call-to-action
- ✅ Engage with comments
- ⏰ Best times: 8 AM, 12 PM, 5 PM

## Tools & Resources

- **OpenTweet:** https://opentweet.io (Twitter automation)
- **Buffer:** https://buffer.com (Multi-platform scheduling)
- **Hootsuite:** https://hootsuite.com (Enterprise social media)
- **Later:** https://later.com (Instagram scheduling)

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
