import { useState, useEffect, useCallback } from 'react';
import PartCard from './components/PartCard';
import './App.css';

const PAGE_SIZE = 48;

// Available sources in the application
const AVAILABLE_SOURCES = ['eBay', 'AliExpress', 'Schmiedmann'];

function App() {
  const [parts, setParts] = useState([]);
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
  }, [skip, isLoading, era, category, selectedSources]);

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

  // Infinite scroll handler
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop < document.documentElement.offsetHeight - 300 || isLoading || !hasMore) {
        return;
      }
      fetchItems();
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [fetchItems, isLoading, hasMore]);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🐐 Cristiano Ronaldo Collectibles</h1>
        <p>Authentic jerseys, memorabilia, and collectibles from the GOAT's legendary career</p>
        
        <div className="filter-section">
          <div className="era-filters">
            <h3>Career Era</h3>
            <div className="filter-buttons">
              <button onClick={() => setEra('')} className={era === '' ? 'active' : ''}>All</button>
              <button onClick={() => setEra('Sporting')} className={era === 'Sporting' ? 'active' : ''}>Sporting</button>
              <button onClick={() => setEra('United')} className={era === 'United' ? 'active' : ''}>United</button>
              <button onClick={() => setEra('Madrid')} className={era === 'Madrid' ? 'active' : ''}>Madrid</button>
              <button onClick={() => setEra('Juventus')} className={era === 'Juventus' ? 'active' : ''}>Juventus</button>
              <button onClick={() => setEra('Portugal')} className={era === 'Portugal' ? 'active' : ''}>Portugal</button>
              <button onClick={() => setEra('Al-Nassr')} className={era === 'Al-Nassr' ? 'active' : ''}>Al-Nassr</button>
            </div>
          </div>
          
          <div className="category-filters">
            <h3>Item Category</h3>
            <div className="filter-buttons">
              <button onClick={() => setCategory('')} className={category === '' ? 'active' : ''}>All</button>
              <button onClick={() => setCategory('jerseys')} className={category === 'jerseys' ? 'active' : ''}>Jerseys</button>
              <button onClick={() => setCategory('boots')} className={category === 'boots' ? 'active' : ''}>Boots</button>
              <button onClick={() => setCategory('memorabilia')} className={category === 'memorabilia' ? 'active' : ''}>Memorabilia</button>
              <button onClick={() => setCategory('signed_items')} className={category === 'signed_items' ? 'active' : ''}>Signed Items</button>
              <button onClick={() => setCategory('cards')} className={category === 'cards' ? 'active' : ''}>Cards</button>
            </div>
          </div>
          
          <div className="source-filters">
            <h3>Sources</h3>
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
          {parts.map(part => (
            <PartCard key={`${part.id}-${part.item_url || part.ebay_url}`} part={part} />
          ))}
        </div>
        {isLoading && <div className="loading-message">Loading Ronaldo items...</div>}
        {!hasMore && <div className="end-of-results">You've reached the end of the collection.</div>}
      </main>
    </div>
  );
}

export default App;
