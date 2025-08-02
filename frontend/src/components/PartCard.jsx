import { useState } from 'react';

function PartCard({ part }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Hebrew translations for common values
  const translateCondition = (condition) => {
    const translations = {
      'New': 'חדש',
      'Used': 'משומש',
      'Vintage': 'ווינטיג',
      'Unknown': 'לא ידוע',
      'Unverified': 'לא מאומת'
    };
    return translations[condition] || condition;
  };

  const toggleDescription = () => {
    setIsExpanded(!isExpanded);
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const description = part.description_he || part.description_en || 'אין תיאור זמין';
  const isLongDescription = description.length > 150;
  const displayDescription = isExpanded ? description : `${description.substring(0, 150)}${isLongDescription ? '...' : ''}`;

  // Determine source and link details
  const source = part.source || 'eBay'; // Default to eBay for backward compatibility
  const isAliExpress = source === 'AliExpress';
  const isSchmiedmann = source === 'Schmiedmann';
  const linkUrl = part.item_url || part.ebay_url; // This field contains the URL regardless of source
  
  let linkText = 'צפה ב-eBay'; // Default
  if (isAliExpress) {
    linkText = 'צפה ב-AliExpress';
  } else if (isSchmiedmann) {
    linkText = 'צפה ב-Schmiedmann';
  }
  
  // Fallback image for missing/broken images
  const fallbackImage = 'https://via.placeholder.com/300x220/e9ecef/6c757d?text=No+Image';

  // Enhanced team color detection
  const getTeamColors = () => {
    const era = part.era?.toLowerCase() || '';
    const title = (part.title_en || '').toLowerCase();
    
    if (era.includes('madrid') || title.includes('real madrid')) {
      return { primary: 'rgba(255, 255, 255, 0.1)', secondary: 'rgba(212, 175, 55, 0.1)' };
    }
    if (era.includes('united') || title.includes('manchester')) {
      return { primary: 'rgba(255, 0, 0, 0.1)', secondary: 'rgba(255, 215, 0, 0.1)' };
    }
    if (era.includes('juventus') || title.includes('juventus')) {
      return { primary: 'rgba(255, 255, 255, 0.1)', secondary: 'rgba(0, 0, 0, 0.1)' };
    }
    if (era.includes('portugal') || title.includes('portugal')) {
      return { primary: 'rgba(255, 0, 0, 0.1)', secondary: 'rgba(0, 100, 0, 0.1)' };
    }
    if (era.includes('sporting') || title.includes('sporting')) {
      return { primary: 'rgba(0, 150, 0, 0.1)', secondary: 'rgba(255, 255, 255, 0.1)' };
    }
    if (era.includes('al-nassr') || title.includes('nassr')) {
      return { primary: 'rgba(255, 215, 0, 0.1)', secondary: 'rgba(0, 0, 255, 0.1)' };
    }
    return { primary: 'rgba(212, 175, 55, 0.05)', secondary: 'rgba(255, 215, 0, 0.05)' };
  };

  const teamColors = getTeamColors();

  return (
    <div 
      className="part-card" 
      style={{
        background: `
          linear-gradient(145deg, ${teamColors.primary}, ${teamColors.secondary}),
          linear-gradient(145deg, rgba(45, 45, 45, 0.9), rgba(58, 58, 58, 0.9))
        `
      }}
    >
      <div className="football-grass-pattern"></div>
      <div className="part-image-container">
        <img 
          src={imageError ? fallbackImage : (part.img_url || fallbackImage)} 
          alt={part.title_en}
          onError={handleImageError}
        />
        <div className={`source-badge ${isAliExpress ? 'aliexpress' : isSchmiedmann ? 'schmiedmann' : 'ebay'}`}>
          {source}
        </div>
        <div className="rarity-indicator">
          {part.price > 500 ? '⭐⭐⭐' : part.price > 200 ? '⭐⭐' : '⭐'}
        </div>
      </div>
      <div className="part-details">
        <div className="part-header">
          <h2>{part.title_en}</h2>
          <div className="item-labels">
            {part.era && <span className="era-label">{part.era}</span>}
            {part.category && <span className="category-label">{part.category}</span>}
            {part.team && <span className="team-label">{part.team}</span>}
            {part.year && <span className="year-label">{part.year}</span>}
            {part.series && <span className="series-label">{part.series}</span>}
          </div>
        </div>
        <p className="description" dir="rtl">
          {displayDescription}
        </p>
        {isLongDescription && (
          <button onClick={toggleDescription} className="read-more-btn">
            {isExpanded ? 'קרא פחות' : 'קרא עוד'}
          </button>
        )}
        <div className="item-info">
          {part.size && <span className="size-info">📏 מידה: {part.size}</span>}
          {part.condition && <span className="condition-info">🔍 מצב: {translateCondition(part.condition)}</span>}
          {part.authenticity && <span className="authenticity-info">✅ אמתות: {translateCondition(part.authenticity)}</span>}
        </div>
        <div className="football-stats">
          <div className="stat-item">
            <span className="stat-icon">⚽</span>
            <span className="stat-label">פריט ספורט</span>
          </div>
          {part.year && (
            <div className="stat-item">
              <span className="stat-icon">📅</span>
              <span className="stat-label">{part.year}</span>
            </div>
          )}
          <div className="stat-item">
            <span className="stat-icon">💎</span>
            <span className="stat-label">
              {part.price > 500 ? 'נדיר' : part.price > 200 ? 'איכותי' : 'נגיש'}
            </span>
          </div>
        </div>
        <p className="price">${part.price}</p>
        <div className="card-actions">
          <a 
            href={linkUrl} 
            target="_blank" 
            rel="noopener noreferrer" 
            className={`marketplace-link ${isAliExpress ? 'aliexpress-link' : isSchmiedmann ? 'schmiedmann-link' : 'ebay-link'}`}
          >
            <span className="action-icon">🛒</span>
            {linkText}
          </a>
          <button 
            className="favorite-btn"
            title="הוסף למועדפים"
            onClick={(e) => {
              e.preventDefault();
              // Add to favorites functionality can be implemented here
              const btn = e.currentTarget;
              btn.classList.toggle('favorited');
              btn.innerHTML = btn.classList.contains('favorited') ? '❤️' : '🤍';
            }}
          >
            🤍
          </button>
        </div>
      </div>
    </div>
  );
}

export default PartCard;
