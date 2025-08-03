import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import PartCard from './components/PartCard';
import StoryBox from './components/StoryBox';
import './App.css';

const PAGE_SIZE = 48;

// Available sources in the application
const AVAILABLE_SOURCES = ['eBay', 'AliExpress', 'Schmiedmann'];

function App() {
  const [parts, setParts] = useState([]);
  const [stories, setStories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [era, setEra] = useState(''); // '' for all, 'Sporting', 'United', 'Madrid', 'Juventus', 'Portugal', 'Al-Nassr'
  const [category, setCategory] = useState(''); // '' for all, 'jerseys', 'boots', 'memorabilia', 'collectibles', 'signed_items', 'cards'
  const [selectedSources, setSelectedSources] = useState(AVAILABLE_SOURCES); // All sources selected by default

  const fetchItems = useCallback(async (newEra = era, newCategory = category, newSources = selectedSources, resetItems = false) => {
    if (isLoading) return;

    setIsLoading(true);
    const currentSkip = (newEra !== era || newCategory !== category || resetItems) ? 0 : skip;
    
    try {
      // Build URL with era, category and source parameters
      const params = new URLSearchParams();
      params.append('skip', currentSkip);
      params.append('limit', PAGE_SIZE);
      
      if (newEra) {
        params.append('era', newEra);
      }
      
      if (newCategory) {
        params.append('category', newCategory);
      }
      
      // If not all sources are selected, add source filters
      if (newSources.length > 0 && newSources.length < AVAILABLE_SOURCES.length) {
        // For multiple sources, we'll fetch from each source and combine client-side
        // This is a limitation of the current API that filters by single source
        // In a production app, the API should support multiple source filtering
      }
      
      let allItems = [];
      
      if (newSources.length === 0) {
        // No sources selected, return empty result
        allItems = [];
      } else if (newSources.length === AVAILABLE_SOURCES.length) {
        // All sources selected, use normal API call
        const url = `/api/items/?${params}`;
        const response = await fetch(url);
        allItems = await response.json();
      } else {
        // Specific sources selected, fetch from each source
        const fetchPromises = newSources.map(async (source) => {
          const sourceParams = new URLSearchParams(params);
          sourceParams.append('source', source);
          const url = `/api/items/?${sourceParams}`;
          const response = await fetch(url);
          return response.json();
        });
        
        const sourceResults = await Promise.all(fetchPromises);
        // Combine and shuffle results from different sources
        allItems = sourceResults.flat();
        
        // Simple shuffle algorithm to mix sources
        for (let i = allItems.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [allItems[i], allItems[j]] = [allItems[j], allItems[i]];
        }
        
        // Apply pagination manually since we're combining results
        const startIndex = currentSkip;
        const endIndex = startIndex + PAGE_SIZE;
        allItems = allItems.slice(startIndex, endIndex);
      }

      if (newEra !== era || newCategory !== category || resetItems) {
        setParts(allItems); // Reset items if era, category or sources changed
      } else {
        setParts(prevParts => [...prevParts, ...allItems]);
      }
      
      if (allItems.length < PAGE_SIZE) {
        setHasMore(false);
      } else {
        setHasMore(true);
        setSkip(currentSkip + PAGE_SIZE);
      }
    } catch (error) {
      console.error("Failed to fetch items:", error);
    } finally {
      setIsLoading(false);
    }
  }, [skip, isLoading]);

  useEffect(() => {
    setParts([]);
    setSkip(0);
    setHasMore(true);
    fetchItems(era, category);
  }, [era, category]);

  // Refetch when sources change
  useEffect(() => {
    setParts([]);
    setSkip(0);
    setHasMore(true);
    fetchItems(era, category, selectedSources, true);
  }, [selectedSources]);

  // Handler for source toggle
  const handleSourceToggle = (source) => {
    setSelectedSources(prev => {
      const newSources = prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source];
      return newSources;
    });
  };

  // Fetch stories based on current filters
  const fetchStories = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (era) params.append('era', era);
      if (category) params.append('category', category);
      
      const response = await fetch(`/api/stories/?${params}`);
      const storiesData = await response.json();
      setStories(storiesData);
    } catch (error) {
      console.error("Failed to fetch stories:", error);
    }
  }, [era, category]);

  // Fetch stories when filters change
  useEffect(() => {
    fetchStories();
  }, [fetchStories]);

  // Handler for finding related items
  const handleFindRelated = useCallback((searchTerms) => {
    const terms = searchTerms.split(',').map(term => term.trim());
    
    // Find the best matching era and category from search terms
    const eras = ['Sporting', 'United', 'Madrid', 'Juventus', 'Portugal', 'Al-Nassr'];
    const categories = ['jerseys', 'boots', 'memorabilia', 'collectibles', 'signed_items', 'cards'];
    
    let foundEra = '';
    let foundCategory = '';
    
    terms.forEach(term => {
      const lowerTerm = term.toLowerCase();
      
      // Check for era matches
      const matchingEra = eras.find(era => 
        era.toLowerCase().includes(lowerTerm) || 
        lowerTerm.includes(era.toLowerCase())
      );
      if (matchingEra) foundEra = matchingEra;
      
      // Check for category matches
      const matchingCategory = categories.find(cat => 
        cat.toLowerCase().includes(lowerTerm) || 
        lowerTerm.includes(cat.toLowerCase())
      );
      if (matchingCategory) foundCategory = matchingCategory;
      
      // Check for team-specific terms
      if (lowerTerm.includes('manchester') || lowerTerm.includes('united')) foundEra = 'United';
      if (lowerTerm.includes('real') || lowerTerm.includes('madrid')) foundEra = 'Madrid';
      if (lowerTerm.includes('juventus') || lowerTerm.includes('juve')) foundEra = 'Juventus';
      if (lowerTerm.includes('portugal')) foundEra = 'Portugal';
      if (lowerTerm.includes('sporting')) foundEra = 'Sporting';
      if (lowerTerm.includes('al-nassr') || lowerTerm.includes('nassr')) foundEra = 'Al-Nassr';
      
      // Check for category-specific terms
      if (lowerTerm.includes('jersey') || lowerTerm.includes('shirt')) foundCategory = 'jerseys';
      if (lowerTerm.includes('boot') || lowerTerm.includes('shoe')) foundCategory = 'boots';
      if (lowerTerm.includes('sign')) foundCategory = 'signed_items';
      if (lowerTerm.includes('card')) foundCategory = 'cards';
    });
    
    // Apply filters and reset items
    if (foundEra && foundEra !== era) {
      setEra(foundEra);
    }
    if (foundCategory && foundCategory !== category) {
      setCategory(foundCategory);
    }
    
    // If we found filters, scroll to top to show new results
    if (foundEra || foundCategory) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [era, category]);

  // Memoized story positions calculation
  const storyPositions = useMemo(() => {
    if (stories.length === 0) return [];
    
    const positions = [];
    let currentPos = 3; // Start at position 3 (after 3 items) for first story
    
    while (currentPos < parts.length) {
      positions.push(currentPos);
      currentPos += 4; // Exactly every 4 items
    }
    
    return positions;
  }, [stories.length, parts.length]);

  // Memoized rendered items with stories
  const renderedElements = useMemo(() => {
    const elements = [];
    
    // If no parts, show stories anyway
    if (parts.length === 0) {
      stories.forEach(story => {
        elements.push(
          <StoryBox 
            key={`story-${story.id}`} 
            story={story} 
            onFindRelated={handleFindRelated}
          />
        );
      });
      return elements;
    }

    // Render parts with stories at calculated positions
    parts.forEach((part, index) => {
      // Add the part
      elements.push(
        <PartCard key={`part-${part.id}-${part.item_url || part.ebay_url}`} part={part} />
      );

      // Check if we should insert a story at this position
      const storyPositionIndex = storyPositions.indexOf(index);
      if (storyPositionIndex !== -1) {
        // Cycle through stories if we have more positions than stories
        const storyIndex = storyPositionIndex % stories.length;
        elements.push(
          <StoryBox 
            key={`story-${stories[storyIndex].id}-pos-${storyPositionIndex}`} 
            story={stories[storyIndex]} 
            onFindRelated={handleFindRelated}
          />
        );
      }
    });

    return elements;
  }, [parts, stories, storyPositions, handleFindRelated]);

  // Throttled scroll handler for better performance
  const scrollTimeoutRef = useRef(null);
  
  useEffect(() => {
    const handleScroll = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      scrollTimeoutRef.current = setTimeout(() => {
        if (window.innerHeight + document.documentElement.scrollTop < document.documentElement.offsetHeight - 300 || isLoading || !hasMore) {
          return;
        }
        fetchItems();
      }, 100); // 100ms throttle
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [fetchItems, isLoading, hasMore]);

  return (
    <div className="App">
      <header className="app-header">
        <div className="football-field-overlay"></div>
        <div className="stadium-lights"></div>
        <h1>🐐 אוסף כריסטיאנו רונאלדו</h1>
        <p>חולצות מקוריות, מזכרות ופריטי אספנות מהקריירה האגדית של ה-GOAT</p>
        <div className="floating-balls">
          <div className="football-ball ball-1">⚽</div>
          <div className="football-ball ball-2">⚽</div>
          <div className="football-ball ball-3">⚽</div>
        </div>
        
        <div className="casual-fan-guide">
          <div className="guide-tip">
            <span className="tip-icon">💡</span>
            <span className="tip-text">בחר תקופה או קטגוריה למציאת פריטי רונאלדו המושלמים!</span>
          </div>
        </div>
        <div className="filter-section">
          <div className="era-filters">
            <h3>
              <span className="filter-icon">🏆</span>
              תקופת קריירה
              <span className="help-tooltip" title="רונאלדו שיחק בקבוצות שונות לאורך הקריירה - כל תקופה יש פריטים ייחודיים">❓</span>
            </h3>
            <div className="filter-buttons">
              <button onClick={() => setEra('')} className={era === '' ? 'active' : ''}>הכל</button>
              <button onClick={() => setEra('Sporting')} className={era === 'Sporting' ? 'active' : ''}>Sporting</button>
              <button onClick={() => setEra('United')} className={era === 'United' ? 'active' : ''}>United</button>
              <button onClick={() => setEra('Madrid')} className={era === 'Madrid' ? 'active' : ''}>Madrid</button>
              <button onClick={() => setEra('Juventus')} className={era === 'Juventus' ? 'active' : ''}>Juventus</button>
              <button onClick={() => setEra('Portugal')} className={era === 'Portugal' ? 'active' : ''}>Portugal</button>
              <button onClick={() => setEra('Al-Nassr')} className={era === 'Al-Nassr' ? 'active' : ''}>Al-Nassr</button>
            </div>
          </div>
          
          <div className="category-filters">
            <h3>
              <span className="filter-icon">⚽</span>
              קטגוריית פריט
              <span className="help-tooltip" title="סוגי פריטים שונים של רונאלדו - מחולצות ועד כרטיסי אספנות">❓</span>
            </h3>
            <div className="filter-buttons">
              <button onClick={() => setCategory('')} className={category === '' ? 'active' : ''}>הכל</button>
              <button onClick={() => setCategory('jerseys')} className={category === 'jerseys' ? 'active' : ''}>חולצות</button>
              <button onClick={() => setCategory('boots')} className={category === 'boots' ? 'active' : ''}>נעליים</button>
              <button onClick={() => setCategory('memorabilia')} className={category === 'memorabilia' ? 'active' : ''}>מזכרות</button>
              <button onClick={() => setCategory('signed_items')} className={category === 'signed_items' ? 'active' : ''}>פריטים חתומים</button>
              <button onClick={() => setCategory('cards')} className={category === 'cards' ? 'active' : ''}>כרטיסים</button>
            </div>
          </div>
          
          <div className="source-filters">
            <h3>
              <span className="filter-icon">🛒</span>
              מקורות
              <span className="help-tooltip" title="בחר מאיזה אתרי קנייה להציג פריטים">❓</span>
            </h3>
            <div className="source-checkboxes">
              {AVAILABLE_SOURCES.map(source => (
                <label key={source} className="source-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source)}
                    onChange={() => handleSourceToggle(source)}
                  />
                  <span className="checkbox-label">{source}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </header>
      <main>
        <div className="items-grid">
          {renderedElements}
        </div>
        {isLoading && (
          <div className="loading-message">
            <div className="loading-content">
              <div className="loading-stadium">
                <div className="loading-field"></div>
                <div className="loading-spinner"></div>
                <div className="bouncing-ball">⚽</div>
              </div>
              <div className="loading-text">
                <span className="loading-dots">טוען פריטי רונאלדו</span>
                <div className="loading-subtitle">מחפש את המזכרות הטובות ביותר...</div>
              </div>
            </div>
          </div>
        )}
        {!hasMore && parts.length > 0 && (
          <div className="end-of-results">
            <div className="end-content">
              <div className="trophy-celebration">
                <div className="trophy-icon">🏆</div>
                <div className="celebration-text">
                  הגעת לסוף האוסף של רונאלדו!
                  <div className="celebration-stats">
                    <span className="stat-item">
                      <span className="stat-icon">📊</span>
                      {parts.length} פריטים נמצאו
                    </span>
                    <span className="stat-item">
                      <span className="stat-icon">⭐</span>
                      חוויית גלישה מושלמת
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        {!isLoading && parts.length === 0 && (
          <div className="no-results">
            <div className="no-results-content">
              ⚽ לא נמצאו פריטים מתאימים
              <p>נסה לשנות את הפילטרים שלך</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
