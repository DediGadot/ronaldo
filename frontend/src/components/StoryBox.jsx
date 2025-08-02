import { useState } from 'react';
import './StoryBox.css';

function StoryBox({ story, onFindRelated }) {
  const [isExpanded, setIsExpanded] = useState(true); // Default to expanded
  const [isLiked, setIsLiked] = useState(false);
  const [shareCount, setShareCount] = useState(Math.floor(Math.random() * 50) + 10);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getStoryIcon = () => {
    const icons = {
      milestone: '🏆',
      record: '📊',
      personal: '❤️',
      quote: '💬',
      trivia: '⚡',
      match: '⚽'
    };
    return icons[story.story_type] || '🌟';
  };

  const getStoryEmojiReactions = () => {
    const reactions = {
      milestone: ['🏆', '🔥', '😍', '🤩'],
      record: ['💪', '😱', '👏', '🤯'],
      personal: ['❤️', '😍', '😭', '🥰'],
      quote: ['💬', '😎', '👍', '🤔'],
      trivia: ['🤯', '😲', '💡', '🤓'],
      match: ['⚽', '🔥', '🎆', '🙌']
    };
    return reactions[story.story_type] || ['👍', '❤️', '😍', '🤩'];
  };

  const getStoryTypeLabel = () => {
    const labels = {
      milestone: 'אבן דרך',
      record: 'שיא',
      personal: 'סיפור אישי',
      quote: 'ציטוט',
      trivia: 'טריוויה',
      match: 'משחק היסטורי'
    };
    return labels[story.story_type] || 'סיפור';
  };

  return (
    <div className="story-box">
      <div className="story-spotlight"></div>
      <div className="story-header">
        <div className="story-icon-container">
          <div className="story-icon">{getStoryIcon()}</div>
          <div className="icon-glow"></div>
        </div>
        <div className="story-meta">
          <span className="story-type">{getStoryTypeLabel()}</span>
          {story.era && <span className="story-era">🏆 {story.era}</span>}
          {story.year && <span className="story-year">📅 {story.year}</span>}
        </div>
        <div className="story-engagement">
          <div className="like-counter">
            <button 
              className={`like-btn ${isLiked ? 'liked' : ''}`}
              onClick={() => setIsLiked(!isLiked)}
            >
              {isLiked ? '❤️' : '🤍'}
            </button>
            <span className="like-count">{isLiked ? shareCount + 1 : shareCount}</span>
          </div>
        </div>
      </div>

      <h3 className="story-title">{story.title_he || story.title_en}</h3>
      
      <div className="story-content">
        <p className="story-summary" dir="rtl">
          {story.summary_he || story.summary_en}
        </p>
        
        {isExpanded && (
          <div className="story-expanded">
            {story.media_url && (
              <div className="story-media">
                <img src={story.media_url} alt={story.title_en} />
              </div>
            )}
            <p className="story-full-content" dir="rtl">
              {story.content_he || story.content_en}
            </p>
            {story.source_url && (
              <a href={story.source_url} target="_blank" rel="noopener noreferrer" className="story-source">
                מקור המידע
              </a>
            )}
          </div>
        )}
      </div>

      <div className="story-reactions">
        <div className="reaction-title">איך הסיפור גרם לך להרגיש?</div>
        <div className="reaction-buttons">
          {getStoryEmojiReactions().map((emoji, index) => (
            <button 
              key={index}
              className="reaction-btn"
              onClick={(e) => {
                e.currentTarget.classList.add('reacted');
                setTimeout(() => e.currentTarget.classList.remove('reacted'), 600);
              }}
            >
              {emoji}
            </button>
          ))}
        </div>
      </div>

      <div className="story-actions">
        <button onClick={toggleExpanded} className="expand-btn">
          <span className="btn-icon">{isExpanded ? '🔼' : '🔽'}</span>
          {isExpanded ? 'הסתר פרטים' : 'קרא סיפור מלא'}
        </button>
        {story.related_search_terms && (
          <button 
            onClick={() => {
              onFindRelated(story.related_search_terms);
              // Add visual feedback
              const btn = document.querySelector('.related-btn');
              if (btn) {
                btn.classList.add('searching');
                setTimeout(() => btn.classList.remove('searching'), 1000);
              }
            }} 
            className="related-btn"
          >
            <span className="btn-icon">🔍</span>
            מצא פריטים קשורים
            <span className="search-indicator"></span>
          </button>
        )}
        <button 
          className="share-btn"
          onClick={() => {
            if (navigator.share) {
              navigator.share({
                title: story.title_he || story.title_en,
                text: story.summary_he || story.summary_en,
                url: window.location.href
              });
            } else {
              // Fallback for browsers without Web Share API
              navigator.clipboard.writeText(window.location.href);
              const btn = document.querySelector('.share-btn');
              if (btn) {
                btn.textContent = '✅ הקישור הועתק!';
                setTimeout(() => {
                  btn.innerHTML = '<span class="btn-icon">🔗</span>שתף סיפור';
                }, 2000);
              }
            }
          }}
        >
          <span className="btn-icon">🔗</span>
          שתף סיפור
        </button>
      </div>

      {/* Enhanced decorative elements */}
      <div className="story-decoration">
        <div className="corner-accent top-left"></div>
        <div className="corner-accent top-right"></div>
        <div className="corner-accent bottom-left"></div>
        <div className="corner-accent bottom-right"></div>
        <div className="floating-elements">
          <div className="float-element element-1">⭐</div>
          <div className="float-element element-2">⚽</div>
          <div className="float-element element-3">🏆</div>
        </div>
      </div>
      
      <div className="story-impact-meter">
        <div className="meter-label">רמת השפעה:</div>
        <div className="meter-bar">
          <div 
            className="meter-fill" 
            style={{
              width: `${story.story_type === 'milestone' ? '95%' : 
                       story.story_type === 'record' ? '90%' :
                       story.story_type === 'match' ? '85%' :
                       story.story_type === 'personal' ? '75%' : '70%'}`
            }}
          ></div>
        </div>
      </div>
    </div>
  );
}

export default StoryBox;