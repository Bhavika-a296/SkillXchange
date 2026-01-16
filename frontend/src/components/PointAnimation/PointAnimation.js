import React, { useEffect, useState } from 'react';
import './PointAnimation.css';

const PointAnimation = ({ points, type, onComplete }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      if (onComplete) {
        onComplete();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!visible) return null;

  const isPositive = points > 0;
  const sign = isPositive ? '+' : '';

  return (
    <div className={`point-animation ${isPositive ? 'positive' : 'negative'} ${type}`}>
      <div className="point-animation-inner">
        <span className="point-value">{sign}{points}</span>
        <span className="point-label">points</span>
      </div>
    </div>
  );
};

export default PointAnimation;
