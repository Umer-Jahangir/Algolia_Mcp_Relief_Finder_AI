// components/DisasterDashboard.jsx
import React, { useEffect, useState } from 'react';
import { Card } from './ui/card.jsx';
import { Alert, AlertDescription } from './ui/alert.jsx';
import { MapPin, AlertTriangle } from 'lucide-react';
import { DisasterSearch } from './ui/DisasterSearch';
import { DisasterMap } from './ui/DisasterMap';

import algoliasearch from 'algoliasearch/lite';

// Use environment variables from Vite
const searchClient = algoliasearch(
  import.meta.env.VITE_ALGOLIA_APP_ID,
  import.meta.env.VITE_ALGOLIA_SEARCH_KEY
);
const index = searchClient.initIndex(import.meta.env.VITE_DISASTER_INDEX_NAME);

export function DisasterDashboard() {
  const [disasters, setDisasters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { hits } = await index.search('', {
          hitsPerPage: 100,
          filters: 'latitude > 0 AND longitude > 0',
        });

        const parsed = hits.map((hit) => ({
          title: hit.title,
          description: hit.description || '',
          latitude: parseFloat(hit.latitude),
          longitude: parseFloat(hit.longitude),
        }));

        setDisasters(parsed);
      } catch (error) {
        console.error('Failed to fetch disaster data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="p-6 pb-24 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Disaster Dashboard</h1>
        <p className="text-gray-600">Real-time alerts in your area</p>
      </div>

      {/* Map Section */}
      <Card className="p-0 bg-slate-100 h-auto rounded-2xl overflow-hidden">
        {loading ? (
          <div className="h-48 flex flex-col items-center justify-center space-y-2">
            <MapPin className="h-12 w-12 text-gray-500" />
            <p>Loading map...</p>
          </div>
        ) : disasters.length > 0 ? (
          <DisasterMap disasters={disasters} />
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-500">
            <p>No disaster alerts found.</p>
          </div>
        )}
      </Card>

      {/* Search and Results */}
      <div className="space-y-4">
        <DisasterSearch />
      </div>

      {/* Emergency Info */}
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-5 w-5 text-red-600" />
        <AlertDescription className="text-red-800">
          <strong>Remember:</strong> In case of immediate danger, call 911 or Disaster Team before using this app.
        </AlertDescription>
      </Alert>
    </div>
  );
}
