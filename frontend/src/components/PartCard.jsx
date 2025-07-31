import { useState } from 'react';

function PartCard({ part }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const toggleDescription = () => {
    setIsExpanded(!isExpanded);
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const description = part.description_he || '';
  const isLongDescription = description.length > 150;
  const displayDescription = isExpanded ? description : `${description.substring(0, 150)}${isLongDescription ? '...' : ''}`;

  // Determine source and link details
  const source = part.source || 'eBay'; // Default to eBay for backward compatibility
  const isAliExpress = source === 'AliExpress';
  const isSchmiedmann = source === 'Schmiedmann';
  const linkUrl = part.item_url || part.ebay_url; // This field contains the URL regardless of source
  
  let linkText = 'View on eBay'; // Default
  if (isAliExpress) {
    linkText = 'View on AliExpress';
  } else if (isSchmiedmann) {
    linkText = 'View on Schmiedmann';
  }
  
  // Fallback image for missing/broken images
  const fallbackImage = 'https://via.placeholder.com/300x220/e9ecef/6c757d?text=No+Image';

  return (
    <div className="part-card">
      <div className="part-image-container">
        <img 
          src={imageError ? fallbackImage : (part.img_url || fallbackImage)} 
          alt={part.title_en}
          onError={handleImageError}
        />
        <div className={`source-badge ${isAliExpress ? 'aliexpress' : isSchmiedmann ? 'schmiedmann' : 'ebay'}`}>
          {source}
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
            {isExpanded ? 'Read Less' : 'Read More'}
          </button>
        )}
        <div className="item-info">
          {part.size && <span className="size-info">Size: {part.size}</span>}
          {part.condition && <span className="condition-info">Condition: {part.condition}</span>}
          {part.authenticity && <span className="authenticity-info">Auth: {part.authenticity}</span>}
        </div>
        <p className="price">${part.price}</p>
        <a 
          href={linkUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={`marketplace-link ${isAliExpress ? 'aliexpress-link' : isSchmiedmann ? 'schmiedmann-link' : 'ebay-link'}`}
        >
          {linkText}
        </a>
      </div>
    </div>
  );
}

export default PartCard;
