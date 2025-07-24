// ReliefFinder.jsx

import React, { useEffect, useState } from 'react';
import algoliasearch from 'algoliasearch/lite';
import { Card } from './ui/card.jsx';
import { Button } from './ui/button.jsx';
import { Badge } from './ui/badge.jsx';
import { Input } from './ui/input.jsx';
import { MapPin, Users, Clock, Phone, Filter, Search } from 'lucide-react';

const searchClient = algoliasearch(
  import.meta.env.VITE_ALGOLIA_APP_ID,
  import.meta.env.VITE_ALGOLIA_SEARCH_KEY
);

const index = searchClient.initIndex(import.meta.env.VITE_RELIEF_INDEX_NAME);

export function ReliefFinder() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [results, setResults] = useState([]);
  const [userLocation, setUserLocation] = useState(null);

  const filters = [
    { id: 'all', label: 'All', query: '', icon: MapPin },
    { id: 'shelter', label: 'Shelter', query: 'type:shelter', icon: MapPin },
    { id: 'food', label: 'Food', query: 'has_food:true', icon: MapPin },
    { id: 'medical', label: 'Medical', query: 'has_medical:true', icon: MapPin },
    { id: 'water', label: 'Water', query: 'has_water:true', icon: MapPin }
  ];

  // Get user's current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setUserLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude
        });
      });
    }
  }, []);

  // Fetch from Algolia
  useEffect(() => {
    const fetchData = async () => {
      const selected = filters.find(f => f.id === selectedFilter);
      const filterQuery = selected?.query || '';

      const { hits } = await index.search(searchQuery, {
        filters: filterQuery,
        hitsPerPage: 50,
      });

      setResults(hits);
    };

    fetchData();
  }, [searchQuery, selectedFilter]);

  // Haversine formula
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const toRad = (val) => (val * Math.PI) / 180;
    const R = 6371; // Earth radius in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'shelter': return 'blue';
      case 'food': return 'green';
      case 'medical': return 'red';
      case 'water': return 'cyan';
      default: return 'gray';
    }
  };

  return (
    <div className="p-6 pb-24 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl">Relief Finder</h1>
        <p>Find help near your location</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          placeholder="Search for specific help..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 h-12"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {filters.map((filter) => (
          <Button
            key={filter.id}
            variant={selectedFilter === filter.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedFilter(filter.id)}
            className="flex-shrink-0"
          >
            <Filter className="mr-1 h-4 w-4" />
            {filter.label}
          </Button>
        ))}
      </div>

      {/* Result Count */}
      <div className="text-sm font-bold">
        Found {results.length} relief options
      </div>

      {/* Results */}
      <div className="space-y-4">
        {results.map((option) => {
const hasCoords = option.latitude && option.longitude;
const distance =
  userLocation && hasCoords
    ? calculateDistance(userLocation.lat, userLocation.lng, option.latitude, option.longitude)
    : null;


          let displayType = 'unknown';
          if (option.has_food) displayType = 'food';
          else if (option.has_water) displayType = 'water';
          else if (option.has_medical) displayType = 'medical';

          const colorClassMap = {
            food: 'bg-green-100 text-green-800',
            water: 'bg-blue-100 text-blue-800',
            medical: 'bg-red-100 text-red-800',
            unknown: 'bg-gray-100 text-gray-800',
          };

          return (
            <Card key={option.objectID} className="p-4 space-y-4">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <h3 className="text-lg">{option.name}</h3>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="secondary"
                      className={`${colorClassMap[displayType]} font-semibold tracking-wide`}
                    >
                      {displayType.toUpperCase()}
                    </Badge>
                    <Badge
                      variant="outline"
                      className={`font-semibold tracking-wide ${
                        option.is_open
                          ? 'text-green-600 border-green-600'
                          : 'text-red-600 border-red-600'
                      }`}
                    >
                      {option.is_open ? 'OPEN' : 'CLOSED'}
                    </Badge>
                  </div>
                </div>

                <div className="text-right text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {distance !== null ? `${distance.toFixed(1)} km` : 'N/A'}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>{option.available_spaces ?? 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    <span>{option.is_24_7 ? '24/7' : 'Limited Hours'}</span>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground">{option.address}</p>

                <div className="flex flex-wrap gap-1">
                  {['has_food', 'has_water', 'has_bed', 'has_medical'].map((key) =>
                    option[key] ? (
                      <Badge key={key} variant="outline" className="text-xs capitalize">
                        {key.replace('has_', '')}
                      </Badge>
                    ) : null
                  )}
                </div>
              </div>

<div className="grid grid-cols-2 gap-2">
  {option.phone_number ? (
    <a href={`tel:${option.phone_number}`} className="w-full">
      <Button variant="outline" size="sm" className="w-full">
        <Phone className="mr-1 h-4 w-4" />
        Call
      </Button>
    </a>
  ) : (
    <Button variant="outline" size="sm" disabled className="w-full">
      <Phone className="mr-1 h-4 w-4" />
      No Number
    </Button>
  )}

  {option.latitude && option.longitude ? (
    <a
      href={`https://www.google.com/maps/dir/?api=1&destination=${option.latitude},${option.longitude}`}
      target="_blank"
      rel="noopener noreferrer"
      className="w-full"
    >
      <Button size="sm" className="w-full">
        <MapPin className="mr-1 h-4 w-4" />
        Get Directions
      </Button>
    </a>
  ) : (
    <Button size="sm" disabled className="w-full">
      <MapPin className="mr-1 h-4 w-4" />
      No Location
    </Button>
  )}
</div>

            </Card>
          );
        })}
      </div>
    </div>
  );
}
