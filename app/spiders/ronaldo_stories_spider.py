import scrapy
import re
from datetime import datetime

class RonaldoStoriesSpider(scrapy.Spider):
    name = "ronaldo_stories"
    
    # Custom settings for respectful scraping
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; RonaldoBot/1.0; +https://ronaldocollectibles.com)',
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': True,
    }
    
    def start_requests(self):
        """Generate requests for various Ronaldo story sources"""
        
        # Wikipedia pages for comprehensive information
        wiki_sources = [
            ("https://en.wikipedia.org/wiki/Cristiano_Ronaldo", "general"),
            ("https://en.wikipedia.org/wiki/Cristiano_Ronaldo_career_statistics", "record"),
            ("https://en.wikipedia.org/wiki/List_of_career_achievements_by_Cristiano_Ronaldo", "milestone"),
        ]
        
        # Official team pages and sports news sites
        news_sources = [
            ("https://www.uefa.com/uefachampionsleague/history/players/63706--cristiano-ronaldo/", "milestone"),
            ("https://www.premierleague.com/players/2522/Cristiano-Ronaldo/overview", "United"),
            ("https://www.realmadrid.com/en/news/2018/07/official-announcement-cristiano-ronaldo", "Madrid"),
        ]
        
        for url, context in wiki_sources + news_sources:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'context': context}
            )
    
    def parse(self, response):
        """Parse response and extract stories based on content type"""
        context = response.meta.get('context', 'general')
        
        if 'wikipedia' in response.url:
            yield from self.parse_wikipedia(response, context)
        elif 'uefa.com' in response.url:
            yield from self.parse_uefa(response)
        elif 'premierleague.com' in response.url:
            yield from self.parse_premier_league(response)
        else:
            # Generic parsing for other sources
            yield from self.parse_generic(response, context)
    
    def parse_wikipedia(self, response, context):
        """Extract stories from Wikipedia pages"""
        
        # Extract milestones and records from tables
        for table in response.css('table.wikitable'):
            headers = table.css('th::text').getall()
            
            # Look for achievement/record tables
            if any(term in ' '.join(headers).lower() for term in ['record', 'achievement', 'milestone', 'goal']):
                for row in table.css('tr')[1:]:  # Skip header row
                    cells = row.css('td')
                    if len(cells) >= 2:
                        achievement = cells[0].css('::text').get()
                        details = ' '.join(cells[1].css('::text').getall())
                        
                        if achievement and details:
                            yield self.create_story(
                                title=achievement.strip(),
                                content=details.strip(),
                                story_type='record',
                                source_url=response.url
                            )
        
        # Extract key career moments from sections
        career_sections = response.css('h2:contains("Career"), h3:contains("Career")').xpath('following-sibling::p[position()<=3]')
        for para in career_sections:
            text = ' '.join(para.css('::text').getall()).strip()
            
            # Look for significant moments
            if any(keyword in text.lower() for keyword in ['first', 'debut', 'record', 'won', 'scored', 'signed']):
                # Extract year if present
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                year = year_match.group() if year_match else None
                
                # Determine era from text
                era = self.determine_era(text)
                
                yield self.create_story(
                    title=self.extract_title_from_text(text),
                    content=text,
                    story_type='milestone',
                    era=era,
                    year=year,
                    source_url=response.url
                )
    
    def parse_uefa(self, response):
        """Extract Champions League achievements"""
        
        # Extract statistics
        stats = response.css('.player-stats__item')
        for stat in stats:
            label = stat.css('.player-stats__label::text').get()
            value = stat.css('.player-stats__value::text').get()
            
            if label and value:
                yield self.create_story(
                    title=f"Champions League {label}: {value}",
                    content=f"Cristiano Ronaldo has achieved {value} {label} in the UEFA Champions League, showcasing his dominance in Europe's premier competition.",
                    story_type='record',
                    category_relevance='jerseys,memorabilia',
                    source_url=response.url
                )
        
        # Extract memorable matches
        matches = response.css('.match-card')
        for match in matches[:5]:  # Top 5 matches
            teams = match.css('.teams::text').get()
            score = match.css('.score::text').get()
            date = match.css('.date::text').get()
            
            if teams and score:
                yield self.create_story(
                    title=f"Memorable Match: {teams}",
                    content=f"On {date}, Ronaldo played a crucial role in the match {teams} that ended {score}.",
                    story_type='match',
                    category_relevance='jerseys,memorabilia,cards',
                    source_url=response.url
                )
    
    def parse_premier_league(self, response):
        """Extract Premier League specific stories"""
        
        # Extract season statistics
        seasons = response.css('.stats-table tbody tr')
        for season in seasons:
            season_text = season.css('td:first-child::text').get()
            goals = season.css('td:contains("Goals") + td::text').get()
            
            if season_text and goals and int(goals) > 20:
                yield self.create_story(
                    title=f"Prolific Season: {season_text}",
                    content=f"Ronaldo scored {goals} goals during the {season_text} Premier League season with Manchester United.",
                    story_type='record',
                    era='United',
                    team='Manchester United',
                    category_relevance='jerseys',
                    source_url=response.url
                )
    
    def create_story(self, **kwargs):
        """Create a story item with default values"""
        
        # Generate summary from content if not provided
        content = kwargs.get('content', '')
        if 'summary' not in kwargs:
            kwargs['summary_en'] = content[:150] + '...' if len(content) > 150 else content
        
        # Set default importance based on story type
        if 'importance_score' not in kwargs:
            importance_map = {
                'milestone': 9,
                'record': 8,
                'match': 7,
                'personal': 6,
                'quote': 5,
                'trivia': 4
            }
            kwargs['importance_score'] = importance_map.get(kwargs.get('story_type', 'trivia'), 5)
        
        # Generate related search terms
        if 'related_search_terms' not in kwargs:
            terms = []
            if kwargs.get('era'):
                terms.append(kwargs['era'])
            if kwargs.get('team'):
                terms.append(kwargs['team'])
            if kwargs.get('year'):
                terms.append(kwargs['year'])
            kwargs['related_search_terms'] = ','.join(terms)
        
        return {
            'title_en': kwargs.get('title', 'Ronaldo Story'),
            'content_en': kwargs.get('content', ''),
            'summary_en': kwargs.get('summary_en', ''),
            'story_type': kwargs.get('story_type', 'trivia'),
            'era': kwargs.get('era'),
            'team': kwargs.get('team'),
            'year': kwargs.get('year'),
            'category_relevance': kwargs.get('category_relevance'),
            'media_url': kwargs.get('media_url'),
            'source_url': kwargs.get('source_url'),
            'importance_score': kwargs.get('importance_score'),
            'related_search_terms': kwargs.get('related_search_terms'),
        }
    
    def determine_era(self, text):
        """Determine era from text content"""
        era_keywords = {
            'Sporting': ['sporting', 'lisbon', 'primeira'],
            'United': ['manchester united', 'old trafford', 'ferguson'],
            'Madrid': ['real madrid', 'bernabeu', 'la liga', 'galactico'],
            'Juventus': ['juventus', 'turin', 'serie a', 'juve'],
            'Portugal': ['portugal', 'selecao', 'euro', 'world cup'],
            'Al-Nassr': ['al-nassr', 'saudi', 'riyadh']
        }
        
        text_lower = text.lower()
        for era, keywords in era_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return era
        return None
    
    def extract_title_from_text(self, text):
        """Extract a meaningful title from paragraph text"""
        # Take first sentence or up to 80 characters
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 80:
                title = title[:77] + '...'
            return title
        return text[:80]
    
    def parse_generic(self, response, context):
        """Generic parsing for other sources"""
        # Extract articles or story sections
        articles = response.css('article, .story, .news-item')
        
        for article in articles[:10]:  # Limit to 10 stories per page
            title = article.css('h1::text, h2::text, h3::text').get()
            content = ' '.join(article.css('p::text').getall())
            image = article.css('img::attr(src)').get()
            
            if title and content:
                yield self.create_story(
                    title=title.strip(),
                    content=content.strip(),
                    story_type=context,
                    media_url=response.urljoin(image) if image else None,
                    source_url=response.url
                )