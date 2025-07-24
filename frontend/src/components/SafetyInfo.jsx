import React, { useEffect, useState } from 'react';
import algoliasearch from 'algoliasearch/lite';
import { Card } from './ui/card.jsx';
import { Button } from './ui/button.jsx';
import { Badge } from './ui/badge.jsx';
import { Progress } from './ui/progress.jsx';
import { Shield, MapPin, Clock, Thermometer, Droplets, Wind, Users, Phone } from 'lucide-react';

const client = algoliasearch(import.meta.env.VITE_ALGOLIA_APP_ID, import.meta.env.VITE_ALGOLIA_SEARCH_KEY);
const reliefIndex = client.initIndex(import.meta.env.VITE_RELIEF_INDEX_NAME);
const OW_KEY = import.meta.env.VITE_OPENWEATHERMAP_KEY;

const fetchWeather = async (lat, lon) => {
  try {
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OW_KEY}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Weather fetch failed:", err);
    return null;
  }
};

const getRiskColor = (risk) => {
  switch (risk) {
    case 'none': return 'green';
    case 'low': return 'yellow';
    case 'medium': return 'orange';
    case 'high': return 'red';
    default: return 'gray';
  }
};

const getScoreColor = (score) => {
  if (score >= 90) return 'green';
  if (score >= 70) return 'yellow';
  if (score >= 50) return 'orange';
  return 'red';
};

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export function SafetyInfo() {
  const [selectedLocation, setSelectedLocation] = useState('current');
  const [currentCoords, setCurrentCoords] = useState(null);
  const [shelter, setShelter] = useState(null);
  const [weatherCurrent, setWeatherCurrent] = useState(null);
  const [weatherShelter, setWeatherShelter] = useState(null);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(async pos => {
      const { latitude, longitude } = pos.coords;
      setCurrentCoords({ latitude, longitude });

      const currentWeather = await fetchWeather(latitude, longitude);
      setWeatherCurrent(currentWeather);

      const { hits } = await reliefIndex.search('', { hitsPerPage: 1000 });

      let closest = null;
      let minDist = Infinity;

      hits.forEach(s => {
        if (s.latitude && s.longitude) {
          const dist = haversineDistance(latitude, longitude, s.latitude, s.longitude);
          if (dist < minDist) {
            minDist = dist;
            closest = s;
          }
        }
      });

      if (closest) {
        setShelter(closest);
        if (closest.latitude && closest.longitude) {
          const ws = await fetchWeather(closest.latitude, closest.longitude);
          setWeatherShelter(ws);
        }
      }
    }, (err) => {
      console.error("Geolocation error:", err);
    });
  }, []);

let currentData = null;

if (selectedLocation === 'current' && currentCoords && weatherCurrent) {
  currentData = {
    name: 'Your Location',
    address: weatherCurrent?.name
      ? `${weatherCurrent.name}, ${weatherCurrent.sys?.country}`
      : `${currentCoords.latitude.toFixed(4)}, ${currentCoords.longitude.toFixed(4)}`,
    safetyScore: 75,
    status: 'Moderate',
    lastUpdated: 'Just now',
    conditions: {
      weather: {
        status: weatherCurrent?.weather?.[0]?.main || 'Unknown',
        risk: 'low',
        icon: Droplets
      },
      temperature: {
        status: `${weatherCurrent?.main?.temp ?? '?'}°C`,
        risk: 'none',
        icon: Thermometer
      },
      wind: {
        status: `${weatherCurrent?.wind?.speed ?? '?'} m/s`,
        risk: 'low',
        icon: Wind
      },
      evacuation: {
        status: 'Not Required',
        risk: 'none',
        icon: Users
      }
    },
    rescueUpdates: [
      { time: '10 min ago', message: 'Team patrolled the area' },
      { time: '30 min ago', message: 'No major threats detected' }
    ],
    recommendations: [
      'Keep updated with weather alerts',
      'Ensure mobile is charged',
      'Inform neighbors of any risks'
    ],
    phone: null
  };
} else if (selectedLocation === 'shelter' && shelter && weatherShelter) {
  currentData = {
    name: shelter.name,
    address: weatherShelter?.name
      ? `${weatherShelter.name}, ${weatherShelter.sys?.country}`
      : `${shelter.latitude?.toFixed(4)}, ${shelter.longitude?.toFixed(4)}`,
    safetyScore: shelter.safetyScore ?? 90,
    status: shelter.status || 'Open',
    lastUpdated: '2 min ago',
    conditions: {
      weather: {
        status: weatherShelter?.weather?.[0]?.main || 'Unknown',
        risk: 'none',
        icon: Droplets
      },
      temperature: {
        status: `${weatherShelter?.main?.temp ?? '?'}°C`,
        risk: 'none',
        icon: Thermometer
      },
      wind: {
        status: `${weatherShelter?.wind?.speed ?? '?'} m/s`,
        risk: 'none',
        icon: Wind
      },
      evacuation: {
        status: 'Safe Zone',
        risk: 'none',
        icon: Users
      }
    },
    rescueUpdates: [
      { time: '5 min ago', message: 'Food delivered' },
      { time: '20 min ago', message: 'Extra bedding supplied' }
    ],
    recommendations: [
      'Rest and hydrate',
      'Wait for further instructions',
      'Cooperate with staff'
    ],
    phone: shelter.phone_number
  };
}


  if (!currentCoords) return <div className="p-6">Locating...</div>;

  return (
    <div className="p-6 pb-24 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Safety Dashboard</h1>
        <p className="text-muted-foreground">Live status and recommendations</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Button variant={selectedLocation === 'current' ? 'default' : 'outline'} onClick={() => setSelectedLocation('current')} className="h-12">
          <MapPin className="mr-2 h-4 w-4" />Current Location
        </Button>
        <Button variant={selectedLocation === 'shelter' ? 'default' : 'outline'} onClick={() => setSelectedLocation('shelter')} className="h-12">
          <Shield className="mr-2 h-4 w-4" />Shelter
        </Button>
      </div>

      {currentData && (
        <>
          <Card className="p-6">
            <div className="space-y-4 text-center">
              <h2 className="text-xl font-semibold">{currentData.name}</h2>
              <p className="text-sm text-muted-foreground">{currentData.address}</p>
              <Badge variant="outline" className={`border-${getScoreColor(currentData.safetyScore)}-500 text-${getScoreColor(currentData.safetyScore)}-700 text-lg px-4 py-2`}>
                {currentData.status}
              </Badge>
              <div className="flex justify-between items-center">
                <span>Safety Score</span>
                <span className="font-semibold">{currentData.safetyScore}/100</span>
              </div>
              <Progress value={currentData.safetyScore} className={`h-3 bg-${getScoreColor(currentData.safetyScore)}-100`} />
              <div className="flex items-center gap-1 text-sm justify-center text-muted-foreground">
                <Clock className="h-4 w-4" />Last updated: {currentData.lastUpdated}
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-lg mb-4">Current Conditions</h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(currentData.conditions).map(([key, condition]) => {
                const Icon = condition.icon;
                return (
                  <div key={key} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium capitalize">{key}</p>
                      <p className="text-xs text-muted-foreground">{condition.status}</p>
                      <Badge variant="outline" className={`text-xs border-${getRiskColor(condition.risk)}-500 text-${getRiskColor(condition.risk)}-700`}>
                        {condition.risk === 'none' ? 'Safe' : `${condition.risk} risk`}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-lg mb-4">Rescue Team Updates</h3>
            <div className="space-y-3">
              {currentData.rescueUpdates.map((update, index) => (
                <div key={index} className="flex gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="text-sm">{update.message}</p>
                    <p className="text-xs text-muted-foreground">{update.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-lg mb-4">Safety Recommendations</h3>
            <div className="space-y-2">
              {currentData.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4 bg-red-50 border-red-200">
            <div className="text-center space-y-3">
              <h3 className="text-red-800">Report Emergency</h3>
              <p className="text-sm text-red-700">If you see immediate danger or need emergency assistance</p>
              <Button
                variant="destructive"
                size="lg"
                className="w-full h-12"
                onClick={() => window.open(`tel:${currentData.phone || '334-9241133'}`)}
              >
                <Phone className="mr-2 h-5 w-5" />Call Disaster Team
              </Button>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
