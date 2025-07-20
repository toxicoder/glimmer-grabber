import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const Collection = () => {
  const [collection, setCollection] = useState([]);

  useEffect(() => {
    const fetchCollection = async () => {
      try {
        const response = await api.get('/collections');
        setCollection(response.data);
      } catch (error) {
        console.error('Error fetching collection:', error);
      }
    };

    fetchCollection();
  }, []);

  return (
    <div>
      <h1>Collection</h1>
      <ul>
        {collection.map((item) => (
          <li key={item.id}>
            {item.name} - {item.card_type}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Collection;
